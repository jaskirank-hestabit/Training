# Deployment Notes

## API

Run:
uvicorn src.deployment.api:app --reload

Endpoint:
POST /predict

## Features

- Input validation using Pydantic
- Request ID tracking
- Prediction logging
- Model version loading

## Monitoring

Run:
python src/monitoring/drift_checker.py

## Docker

Build:
docker build -t titanic-api -f src/deployment/Dockerfile .

Run:
docker run -p 8000:8000 titanic-api