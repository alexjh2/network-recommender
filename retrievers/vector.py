from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QDRANT_PATH = "data/tmp/my_qdrant_data"   # <- consistent embedded storage
COLLECTION = "user_embeddings"

def find_similar_bios(qdrant_path=str(QDRANT_PATH), collection_name=COLLECTION, query_text="", top_k=3):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = QdrantClient(path=qdrant_path)           # embedded mode
    query_vector = model.encode(query_text).tolist()

    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True
    )
    return results
