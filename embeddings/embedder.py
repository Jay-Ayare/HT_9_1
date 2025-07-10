from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        print("embedder.py loaded")

    def get_embedding(self, text: str):
        return self.model.encode(text, normalize_embeddings=True)

    def get_embeddings(self, texts: list[str]):
        return self.model.encode(texts, normalize_embeddings=True)
