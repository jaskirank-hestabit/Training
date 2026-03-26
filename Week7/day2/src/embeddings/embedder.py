import yaml
from sentence_transformers import SentenceTransformer

# Load config
with open("src/config/model.yaml") as f:
    config = yaml.safe_load(f)

MODEL_NAME = config["embedding"]["model_name"]

print(f"Loading embedding model: {MODEL_NAME}")

model = SentenceTransformer(MODEL_NAME)


def get_embeddings(texts):
    return model.encode(texts, normalize_embeddings=True).tolist()


def get_query_embedding(text):
    return model.encode([text], normalize_embeddings=True).tolist()[0]