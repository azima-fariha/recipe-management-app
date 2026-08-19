import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PayloadSchemaType, VectorParams

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")

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

# Indexed so filtering by user_id (see vector_service.retrieve_similar_texts_with_filtering)
# doesn't fall back to a full collection scan. create_payload_index is idempotent - safe to
# call every time the service starts.
client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="metadata.user_id",
    field_schema=PayloadSchemaType.KEYWORD,
)

def get_qdrant_client() -> QdrantClient:
    return client
