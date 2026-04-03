# Lab 2 Submission README
# Sorry it's not in the submission folder whoops

## Student Information
- Name: Jordan Ehrman
- Date: 2026-04-02

## Deliverables Included
- `inference_api/Dockerfile`
- `preprocessor/Dockerfile`
- `inference_api/app.py` (with `/health` and `/stats`)
- `sample_classifications_20.jsonl` (first 20 lines from logs)
- `Reflection.md`

## Docker Build Commands Used

### Inference API
```bash
docker build -t congo-inference ./inference_api
```

### Preprocessor
```bash
docker build -t congo-preprocessor ./preprocessor
```

## Docker Run Commands Used

### Inference API Container
```bash
docker run --name congo-inference-container \
  -p 8000:8000 \
  -v "$(pwd)/logs:/logs" \
  congo-inference
```

### Preprocessor Container
```bash
docker run --name congo-preprocessor-container \
  -v "$(pwd)/incoming:/incoming" \
  -e API_URL=http://host.docker.internal:8000 \
  congo-preprocessor
```

## Brief Explanation: How the Containers Communicate
The preprocessor polls /incoming for image files, extracts metadata from filenames, and sends each image to the inference API using the API_URL environment variable. The inference API classifies the image and writes the result to /logs/classifications.jsonl, which is persisted through a bind mount. Successful images are moved into /incoming/processed.
