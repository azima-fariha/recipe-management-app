import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PayloadSchemaType, VectorParams

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")

COLLECTION_NAME = "recipes"
VECTOR_SIZE = 3072 

client = QdrantClient(url=QDRANT_URL)

if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="metadata.user_id",
    field_schema=PayloadSchemaType.KEYWORD,
)

def get_qdrant_client() -> QdrantClient:
    return client
