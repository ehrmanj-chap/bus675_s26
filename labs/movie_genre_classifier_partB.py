"""
Lab 3 - Part B: Multimodal Movie Genre Classifier with ResNet18
================================================================
This file keeps the completed Part A structure, but replaces only ImageBranch
with a ResNet18 transfer-learning branch.
"""

import json
import os
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from tqdm import tqdm


GENRES = ["Animation", "Comedy", "Documentary", "Horror", "Romance", "Sci-Fi"]

NUMERIC_COLS = ["runtime", "vote_average", "vote_count",
                "release_year", "popularity", "budget", "revenue"]

LIST_FIELDS = ["cast", "directors", "writers", "production_companies"]
SINGLE_CAT_FIELDS = ["mpaa_rating"]

IMAGE_SIZE   = 128
MAX_LIST_LEN = 20
TOP_N_VOCAB  = 50
EMBED_DIM    = 32


class VocabBuilder:
    """
    Builds integer vocabularies for pipe-separated categorical fields.
    Fit only on training data.
    """

    PAD_IDX = 0
    UNK_IDX = 1

    def __init__(self, top_n=TOP_N_VOCAB):
        self.top_n  = top_n
        self.vocabs = {}
        self.sizes  = {}

    def fit(self, df):
        for field in LIST_FIELDS:
            if field not in df.columns:
                continue
            counts = Counter()
            for val in df[field].dropna():
                if val:
                    counts.update(v.strip() for v in str(val).split("|") if v.strip())
            top_tokens = [tok for tok, _ in counts.most_common(self.top_n)]
            vocab = {tok: idx + 2 for idx, tok in enumerate(top_tokens)}
            self.vocabs[field] = vocab
            self.sizes[field]  = len(vocab) + 2

        for field in SINGLE_CAT_FIELDS:
            if field not in df.columns:
                continue
            unique_vals = [v for v in df[field].unique()
                           if isinstance(v, str) and v.strip()]
            vocab = {v: idx + 2 for idx, v in enumerate(sorted(unique_vals))}
            self.vocabs[field] = vocab
            self.sizes[field]  = len(vocab) + 2
        return self

    def encode_list(self, val, field, max_len=MAX_LIST_LEN):
        vocab = self.vocabs.get(field, {})
        if not isinstance(val, str) or not val.strip():
            return [self.PAD_IDX] * max_len
        tokens = [v.strip() for v in val.split("|") if v.strip()]
        ids = [vocab.get(tok, self.UNK_IDX) for tok in tokens]
        ids = ids[:max_len]
        ids += [self.PAD_IDX] * (max_len - len(ids))
        return ids

    def encode_single(self, val, field):
        vocab = self.vocabs.get(field, {})
        if not isinstance(val, str) or not val.strip():
            return self.PAD_IDX
        return vocab.get(val.strip(), self.UNK_IDX)

    def save(self, path):
        data = {"vocabs": self.vocabs, "sizes": self.sizes, "top_n": self.top_n}
        Path(path).write_text(json.dumps(data))

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text())
        vb = cls(top_n=data["top_n"])
        vb.vocabs = data["vocabs"]
        vb.sizes  = data["sizes"]
        return vb


class NumericScaler:
    """
    Standardises numeric features to zero mean, unit variance.
    Fit on training data only. Missing values are imputed with the training mean.
    """

    def __init__(self):
        self.means = {}
        self.stds  = {}

    def fit(self, df):
        for col in NUMERIC_COLS:
            if col in df.columns:
                vals = pd.to_numeric(df[col], errors="coerce")
                self.means[col] = float(vals.mean())
                self.stds[col]  = max(float(vals.std()), 1e-8)
        return self

    def transform(self, df):
        result = {}
        for col in NUMERIC_COLS:
            vals = pd.to_numeric(df[col], errors="coerce") if col in df.columns \
                   else pd.Series([float("nan")] * len(df))
            vals = vals.fillna(self.means.get(col, 0.0))
            mean = self.means.get(col, 0.0)
            std  = self.stds.get(col, 1.0)
            result[col] = ((vals - mean) / std).values.astype(np.float32)
        return result

    def save(self, path):
        Path(path).write_text(json.dumps({"means": self.means, "stds": self.stds}))

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text())
        ns = cls()
        ns.means = data["means"]
        ns.stds  = data["stds"]
        return ns


class MoviePosterDataset(Dataset):
    """
    Loads a split and returns poster image, numeric features,
    categorical fields, and genre label for one film.
    """

    def __init__(self, df, image_dir, vocab_builder, numeric_scaler,
                 transform=None):
        self.df = df.reset_index(drop=True)
        self.image_dir = Path(image_dir)
        self.vocab_builder = vocab_builder
        self.numeric_scaler = numeric_scaler
        self.transform = transform
        self.image_col = "image_path"
        self.label_col = "label"
        self.genre_to_idx = {genre: idx for idx, genre in enumerate(GENRES)}
        numeric_dict = self.numeric_scaler.transform(self.df)
        self.numeric_matrix = np.stack(
            [numeric_dict[col] for col in NUMERIC_COLS],
            axis=1
        ).astype(np.float32)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = self.image_dir / str(row[self.image_col])
        image = Image.open(img_path).convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
        numeric = torch.tensor(self.numeric_matrix[idx], dtype=torch.float32)
        cat_fields = {}

        for field in LIST_FIELDS:
            encoded = self.vocab_builder.encode_list(row.get(field, ""), field)
            cat_fields[field] = torch.tensor(encoded, dtype=torch.long)

        for field in SINGLE_CAT_FIELDS:
            encoded = self.vocab_builder.encode_single(row.get(field, ""), field)
            cat_fields[field] = torch.tensor(encoded, dtype=torch.long)

        label_name = row[self.label_col]
        label = torch.tensor(self.genre_to_idx[label_name], dtype=torch.long)

        return {
            "image": image,
            "numeric": numeric,
            "cat_fields": cat_fields,
            "label": label,
        }


class ImageBranch(nn.Module):
    """
    Part B image encoder: pretrained ResNet18 backbone with a small trainable head.
    The backbone is frozen by default; only the projection head trains.
    """

    BACKBONE_OUT_DIM = 512

    def __init__(self, out_dim=256, dropout=0.4, fine_tune=False):
        super().__init__()

        backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

        for param in backbone.parameters():
            param.requires_grad = False

        if fine_tune:
            for param in backbone.layer4.parameters():
                param.requires_grad = True

        self.backbone = nn.Sequential(*list(backbone.children())[:-1])
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(dropout),
            nn.Linear(self.BACKBONE_OUT_DIM, out_dim),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        features = self.backbone(x)
        return self.head(features)


class TabularBranch(nn.Module):
    """
    Takes numeric features and categorical embeddings and produces a feature vector.
    """

    def __init__(self, vocab_sizes, out_dim=256):
        super().__init__()
        self.list_fields = [field for field in LIST_FIELDS if field in vocab_sizes]
        self.single_cat_fields = [field for field in SINGLE_CAT_FIELDS if field in vocab_sizes]
        self.all_cat_fields = self.list_fields + self.single_cat_fields

        self.embeddings = nn.ModuleDict({
            field: nn.Embedding(
                num_embeddings=vocab_sizes[field],
                embedding_dim=EMBED_DIM,
                padding_idx=VocabBuilder.PAD_IDX,
            )
            for field in self.all_cat_fields
        })

        self.numeric_net = nn.Sequential(
            nn.Linear(len(NUMERIC_COLS), 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(64, 64),
            nn.ReLU(inplace=True),
        )

        cat_input_dim = max(len(self.all_cat_fields), 1) * EMBED_DIM
        self.cat_net = nn.Sequential(
            nn.Linear(cat_input_dim, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, 128),
            nn.ReLU(inplace=True),
        )

        self.merge = nn.Sequential(
            nn.Linear(64 + 128, out_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
        )

    def _mean_pool_list_embedding(self, token_ids, embedding_layer):
        emb = embedding_layer(token_ids)
        mask = (token_ids != VocabBuilder.PAD_IDX).float().unsqueeze(-1)
        summed = (emb * mask).sum(dim=1)
        counts = mask.sum(dim=1).clamp(min=1.0)
        return summed / counts

    def forward(self, numeric, cat_fields):
        numeric_features = self.numeric_net(numeric)
        pooled_embeddings = []

        for field in self.list_fields:
            token_ids = cat_fields[field]
            pooled = self._mean_pool_list_embedding(token_ids, self.embeddings[field])
            pooled_embeddings.append(pooled)

        for field in self.single_cat_fields:
            token_ids = cat_fields[field]
            emb = self.embeddings[field](token_ids)
            pooled_embeddings.append(emb)

        if len(pooled_embeddings) == 0:
            batch_size = numeric.shape[0]
            cat_features_raw = torch.zeros(
                batch_size,
                EMBED_DIM,
                device=numeric.device,
                dtype=numeric.dtype,
            )
        else:
            cat_features_raw = torch.cat(pooled_embeddings, dim=1)

        cat_features = self.cat_net(cat_features_raw)
        merged = torch.cat([numeric_features, cat_features], dim=1)
        return self.merge(merged)


class FusionHead(nn.Module):
    """
    Concatenates image and tabular feature vectors and predicts genre.
    Output: (batch, num_classes) logits.
    """

    def __init__(self, image_dim, tabular_dim, num_classes=len(GENRES)):
        super().__init__()
        self.classifier = nn.Sequential(
            nn.Linear(image_dim + tabular_dim, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
            nn.Linear(256, num_classes),
        )

    def forward(self, image_features, tabular_features):
        fused = torch.cat([image_features, tabular_features], dim=1)
        return self.classifier(fused)


class MultimodalGenreClassifier(nn.Module):
    """Wires ImageBranch, TabularBranch, and FusionHead together."""

    def __init__(self, vocab_sizes):
        super().__init__()
        image_dim = 256
        tabular_dim = 256
        self.image_branch = ImageBranch(out_dim=image_dim)
        self.tabular_branch = TabularBranch(vocab_sizes, out_dim=tabular_dim)
        self.fusion_head = FusionHead(
            image_dim=image_dim,
            tabular_dim=tabular_dim,
            num_classes=len(GENRES),
        )

    def forward(self, image, numeric, cat_fields):
        image_features = self.image_branch(image)
        tabular_features = self.tabular_branch(numeric, cat_fields)
        logits = self.fusion_head(image_features, tabular_features)
        return logits


def move_batch_to_device(batch, device):
    image = batch["image"].to(device)
    numeric = batch["numeric"].to(device)
    cat_fields = {k: v.to(device) for k, v in batch["cat_fields"].items()}
    label = batch["label"].to(device)
    return image, numeric, cat_fields, label


def accuracy_from_logits(logits, labels):
    preds = logits.argmax(dim=1)
    correct = (preds == labels).sum().item()
    total = labels.numel()
    return correct, total


def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    running_loss = 0.0
    running_correct = 0
    running_total = 0
    for batch in tqdm(loader, desc="Training", leave=False):
        image, numeric, cat_fields, label = move_batch_to_device(batch, device)
        optimizer.zero_grad()
        logits = model(image, numeric, cat_fields)
        loss = criterion(logits, label)
        loss.backward()
        optimizer.step()
        correct, total = accuracy_from_logits(logits, label)
        running_loss += loss.item() * total
        running_correct += correct
        running_total += total
    avg_loss = running_loss / max(running_total, 1)
    avg_acc = running_correct / max(running_total, 1)
    return avg_loss, avg_acc


@torch.no_grad()
def evaluate(model, loader, criterion, device, desc="Evaluating"):
    model.eval()
    running_loss = 0.0
    running_correct = 0
    running_total = 0
    for batch in tqdm(loader, desc=desc, leave=False):
        image, numeric, cat_fields, label = move_batch_to_device(batch, device)
        logits = model(image, numeric, cat_fields)
        loss = criterion(logits, label)
        correct, total = accuracy_from_logits(logits, label)
        running_loss += loss.item() * total
        running_correct += correct
        running_total += total
    avg_loss = running_loss / max(running_total, 1)
    avg_acc = running_correct / max(running_total, 1)
    return avg_loss, avg_acc


@torch.no_grad()
def per_class_accuracy(model, loader, device):
    model.eval()
    correct_by_class = {genre: 0 for genre in GENRES}
    total_by_class = {genre: 0 for genre in GENRES}
    overall_correct = 0
    overall_total = 0
    for batch in tqdm(loader, desc="Per-class accuracy", leave=False):
        image, numeric, cat_fields, label = move_batch_to_device(batch, device)
        logits = model(image, numeric, cat_fields)
        preds = logits.argmax(dim=1)
        for true_idx, pred_idx in zip(label.cpu().tolist(), preds.cpu().tolist()):
            genre = GENRES[true_idx]
            total_by_class[genre] += 1
            overall_total += 1
            if pred_idx == true_idx:
                correct_by_class[genre] += 1
                overall_correct += 1
    acc_by_class = {}
    for genre in GENRES:
        total = total_by_class[genre]
        correct = correct_by_class[genre]
        acc_by_class[genre] = correct / total if total > 0 else 0.0
    overall_acc = overall_correct / overall_total if overall_total > 0 else 0.0
    return acc_by_class, overall_acc
