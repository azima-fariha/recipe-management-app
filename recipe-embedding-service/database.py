from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

QDRANT_URL = "http://localhost:6333"

COLLECTION_NAME = "recipes"
VECTOR_SIZE = 3072  # output dimension of text-embedding-3-large

client = QdrantClient(url=QDRANT_URL)

# Collections are created lazily, similar to how Mongo creates its
# database/collection on first write - here Qdrant needs the vector
# size/distance metric declared upfront, so this runs once at import time.
if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

def get_qdrant_client() -> QdrantClient:
    return client
