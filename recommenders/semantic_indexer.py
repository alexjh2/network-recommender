import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

PARSED_BIOS_PATH = "data/parsed_bios.jsonl"
QDRANT_COLLECTION_NAME = "user_embeddings"
MODEL_NAME = "all-MiniLM-L6-v2"

def load_bios(file_path):
    with open(file_path, "r") as f:
        return [json.loads(line) for line in f]

def main():
    bios = load_bios(PARSED_BIOS_PATH)
    if not bios:
        print("No bios loaded.")
        return
    print(f"Loaded {len(bios)} bios")

    model = SentenceTransformer(MODEL_NAME)
    print("Model loaded.")

    bio_texts = [bio["bio"] for bio in bios]
    vectors = model.encode(bio_texts, show_progress_bar=True)

    client = QdrantClient(path="../data/tmp/my_qdrant_data")
    vector_size = len(vectors[0])

    client.recreate_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
    )
    print(f"Collection '{QDRANT_COLLECTION_NAME}' created with {vector_size}-dim vectors")

    points = [
        models.PointStruct(
            id=int(bio["user_id"]),
            vector=vector.tolist() if hasattr(vector, "tolist") else vector,
            payload=bio
        )
        for bio, vector in zip(bios, vectors)
    ]

    client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=points
    )
    print("All vectors upserted")

    query_text = "Software Engineer currently working at Google who graduated from CMU"
    query_vector = model.encode(query_text).tolist()

    print(f"\nSearching for bios similar to: '{query_text}'")
    results = client.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=query_vector,
        limit=3,
        with_payload=True
    )

    print("\nTop Matches:")
    for r in results:
        print(f"  Score: {r.score:.4f}")
        print(f"  Bio: {r.payload['bio'][:200]}...")
        print(f"  Sources: {r.payload['sources']}")
        print("-" * 40)

if __name__ == "__main__":
    main()














"""
import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
import os

JSONL_FILE_PATH = 'bios.jsonl'
QDRANT_COLLECTION_NAME = 'user_bios'
SENTENCE_TRANSFORMER_MODEL = 'all-MiniLM-L6-v2'

dummy_jsonl_content = """
{"id": 1, "name": "Alice", "bio": "Alice is a software engineer passionate about open source and machine learning."}
{"id": 2, "name": "Bob", "bio": "Bob is a data scientist specializing in natural language processing and vector databases."}
{"id": 3, "name": "Charlie", "bio": "Charlie enjoys hiking, photography, and building web applications."}
{"id": 4, "name": "Diana", "bio": "Diana is a machine learning researcher focused on computer vision and deep learning."}
{"id": 5, "name": "Eve", "bio": "Eve is a product manager with a background in AI and user experience design."}
{"id": 6, "name": "Frank", "bio": "Frank is an artist who creates abstract paintings and digital art."}
{"id": 7, "name": "Grace", "bio": "Grace is a musician who plays classical piano and composes electronic music."}
{"id": 8, "name": "Heidi", "bio": "Heidi is a chef known for her innovative fusion cuisine and culinary workshops."}
{"id": 9, "name": "Ivan", "bio": "Ivan is a writer of science fiction novels and short stories."}
{"id": 10, "name": "Judy", "bio": "Judy is a fitness instructor who specializes in yoga and high-intensity interval training."}
"""

def create_dummy_jsonl_file(file_path, content):
    print(f"Creating dummy JSONL file: {file_path}")
    with open(file_path, 'w') as f:
        f.write(content.strip())

def load_bios_from_jsonl(file_path):
    bios_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    bios_data.append(json.loads(line.strip()))
                except json.JSONDecodeError as e:
                    print(f"Skipping malformed JSON line: {line.strip()} - Error: {e}")
    except FileNotFoundError:
        print(f"Error: JSONL file not found at {file_path}")
        return []
    return bios_data

def main():
    create_dummy_jsonl_file(JSONL_FILE_PATH, dummy_jsonl_content)
    bios = load_bios_from_jsonl(JSONL_FILE_PATH)
    if not bios:
        print("No bios loaded. Exiting")
        return
    print(f"Loaded {len(bios)} bios from {JSONL_FILE_PATH}")
    
    print(f"Loading SentenceTransformer model: {SENTENCE_TRANSFORMER_MODEL}...")
    model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
    print("Model loaded")

    bio_texts = [bio["bio"] for bio in bios]
    print(f"Generating embeddings for {len(bio_texts)} bios")
    vectors = model.encode(bio_texts, show_progress_bar=True)
    print("Embeddings generated.")
    print(f"Vector dimension: {vectors.shape[1]}")

    print("Initializing Qdrant in-memory client...")
    client = QdrantClient(":memory:")

    vector_size = vectors.shape[1]
    print(f"Creating collection '{QDRANT_COLLECTION_NAME}' with vector size {vector_size}...")
    client.recreate_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
    )
    print("Collection created")

    points = []
    for i, bio_data in enumerate(bios):
        points.append(
            models.PointStruct(
                id=i, # Unique ID for each point
                vector=vectors[i].tolist(), # Convert numpy array to list
                payload=bio_data # Store the original bio dictionary as payload
            )
        )

    print(f"Upserting {len(points)} points to Qdrant collection '{QDRANT_COLLECTION_NAME}'...")
    client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        wait=True, # Wait for the operation to complete
        points=points
    )
    print("Points upserted successfully.")

    print("\n--- Performing an example search ---")
    query_text = "machine learning expert"
    query_vector = model.encode(query_text).tolist()

    print(f"Searching for bios similar to: '{query_text}'")
    search_results = client.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=query_vector,
        limit=3, # Get top 3 results
        with_payload=True # Retrieve the original metadata
    )

    print("\nSearch Results:")
    for result in search_results:
        print(f"  Score: {result.score:.4f}")
        print(f"  Bio: {result.payload['bio']}")
        print(f"  Name: {result.payload['name']}")
        print("-" * 20)
    
    if os.path.exists(JSONL_FILE_PATH):
        os.remove(JSONL_FILE_PATH)
        print(f"\nCleaned up dummy JSONL file: {JSONL_FILE_PATH}")

if __name__ == "__main__":
    main()
"""
