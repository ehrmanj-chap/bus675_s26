| Genre | Part A Accuracy | Part B Accuracy |
|---|---:|---:|
| Animation | 0.807 | 0.840 |
| Comedy | 0.660 | 0.660 |
| Documentary | 0.827 | 0.847 |
| Horror | 0.773 | 0.813 |
| Romance | 0.607 | 0.733 |
| Sci-Fi | 0.660 | 0.607 |
| **Overall** | **0.722** | **0.750** |

## 1. Architecture choices

For Part A, I used a multimodal architecture with three main components: a custom convolutional image branch, a tabular branch, and a fusion classifier. The image branch used several `Conv2d` blocks with batch normalization, ReLU activations, max pooling, and a final adaptive average pooling layer. This let the model learn spatial poster features without flattening the image directly into a fully connected layer. After the convolutional layers, I projected the image representation into a 256-dimensional feature vector.

The tabular branch had two sub-branches. The numeric branch took standardized features such as runtime, vote average, vote count, release year, popularity, budget, and revenue, then passed them through a small fully connected network. The categorical branch used learned embeddings for the pipe-separated list fields: cast, directors, writers, and production companies, plus a separate embedding for MPAA rating. For the list fields, I mean-pooled the token embeddings so each movie had one fixed-size vector per metadata field. These categorical embeddings were concatenated and passed through another small fully connected network. Finally, I concatenated the image and tabular feature vectors and passed them through a fusion head to predict one of the six genres.

I chose this structure because it separated the two kinds of information in the data: visual poster information and structured metadata. The image branch could focus on color, composition, and visual genre cues, while the tabular branch could learn patterns from metadata such as rating, popularity, release year, and repeated names in cast or production information. I kept the model relatively small because the training set was modest in size and the goal was to get a clean baseline without excessive overfitting.

I did not do an extensive architecture search. The main design choice was to use a simple custom CNN for Part A rather than a larger model. I also avoided making the categorical vocabulary too large, since fields like cast and production companies contain many unique values and could easily lead to memorization rather than generalization.

## 2. Overfitting

I did not observe severe overfitting during the five-epoch Part A run. In Part A, training accuracy increased from 0.551 to 0.744, while validation accuracy increased from 0.680 to 0.767. The validation accuracy stayed slightly above the training accuracy throughout training, which may be due to dropout and data augmentation being active during training but disabled during evaluation.

For Part B, training accuracy increased from 0.568 to 0.764, while validation accuracy increased from 0.693 to a peak of 0.773 at epoch 4, then slightly decreased to 0.769 at epoch 5. This small drop suggests the model may have started to plateau or very mildly overfit near the end, but the effect was not large.

The main strategies I used to reduce overfitting were dropout, weight decay through AdamW, a limited top-N vocabulary for categorical fields, and a relatively small custom CNN in Part A. I also saved the best checkpoint based on validation accuracy rather than simply using the final epoch. The most effective strategy seemed to be keeping the model size controlled and using validation checkpointing. Dropout likely also helped, especially because the training accuracy stayed lower than validation accuracy.

## 3. Part A vs. Part B

The pretrained ResNet18 model in Part B performed better overall than the custom CNN in Part A. Part A reached an overall test accuracy of 0.722, while Part B reached 0.750. Transfer learning therefore improved the overall result by about 2.8 percentage points.

Part B improved accuracy for Animation, Documentary, Horror, and especially Romance. Romance increased from 0.607 in Part A to 0.733 in Part B, which was the largest class-level improvement. Documentary also improved from 0.827 to 0.847, Horror from 0.773 to 0.813, and Animation from 0.807 to 0.840. Comedy stayed the same at 0.660. Sci-Fi was the only genre that got worse, dropping from 0.660 to 0.607.

Transfer learning helped because the ResNet18 backbone already had useful general-purpose visual features from ImageNet pretraining. Even though movie posters are not the same as ImageNet images, pretrained convolutional filters are still useful for edges, textures, shapes, objects, faces, and composition. Since the backbone was mostly frozen and only the projection head was trained, Part B could use a stronger visual representation without needing to learn all image features from scratch. This likely made it more stable and sample-efficient than the custom CNN.

## 4. Tabular branch insights

The metadata features seemed very important for this task. The model reached fairly strong accuracy even with a simple architecture, suggesting that structured features such as runtime, release year, popularity, vote count, MPAA rating, cast, directors, writers, and production companies carried substantial genre signal. Some genres are strongly associated with metadata patterns. For example, Animation often has shorter runtimes, different rating distributions, and recognizable production companies. Documentary can also have distinctive popularity, budget, release, and cast/director patterns compared with fiction genres.

Looking at the per-class accuracy table, the Part A model struggled most with Romance, which had an accuracy of 0.607. It also had lower performance on Comedy and Sci-Fi, both at 0.660. This makes sense because Comedy and Romance can be visually and structurally broad. A romantic comedy poster may resemble either Romance or Comedy, and many movies mix these genres. Sci-Fi can also overlap visually with Horror, Action, or Animation depending on the poster style and metadata.

Part B improved Romance substantially, which suggests that the pretrained image features helped capture visual poster cues that the smaller custom CNN missed. However, Sci-Fi performance decreased in Part B, so the pretrained visual representation was not uniformly better for every class. This could mean the frozen ResNet features helped with general poster style but did not specialize enough for some genre-specific visual patterns.

I did not run full tabular-only or image-only ablation experiments. If I had, they would have helped separate how much of the performance came from posters versus metadata. Based on the results, I suspect the tabular branch was carrying a large part of the prediction signal, while the image branch helped refine classes where poster style was especially informative.

## 5. What would you do differently?

With more compute time or training data, I would first run ablation experiments: image-only, tabular-only, and multimodal models. That would make it clearer how much each modality contributed. I would also try fine-tuning the last ResNet block after the projection head had converged, since the Part B backbone was frozen by default. This might improve genre-specific visual features, especially for classes like Sci-Fi.

I would also experiment with larger or better-controlled categorical vocabularies. The top-50 vocabulary keeps the model small, but it may discard useful recurring information from actors, directors, writers, and production companies. A larger vocabulary, stronger regularization, or frequency thresholds could improve the tabular branch without simply memorizing rare names.

Finally, I would try better image augmentation and possibly class-balanced loss or sampling if the model struggled unevenly across genres. The per-class results show that performance was not uniform, so class-specific errors are important. More training epochs with early stopping and a learning rate scheduler could also improve performance while still avoiding overfitting.