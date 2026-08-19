from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import FieldCondition, Filter, MatchValue
from database import COLLECTION_NAME, get_qdrant_client
import uuid
import logging
from schemas import RecipeCreatedEvent

load_dotenv()

logger = logging.getLogger(__name__)

TOP_K = 2  # Number of similar texts to retrieve
SCORE_THRESHOLD = 0.35  # Minimum cosine similarity for a match to be considered relevant


client = get_qdrant_client()

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")  # Initialize OpenAI embeddings

vector_store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
)

def point_id(recipe_id: str) -> str:
    """Generate a unique point ID for the given recipe ID."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, recipe_id))

def vectorize_recipe(recipe: RecipeCreatedEvent):
    """Generate embeddings for the given text and store them in Qdrant."""
    logger.info("Generating and storing embeddings for recipe id:%s", recipe.id)
    text = recipe.to_embedding_text()
    id = vector_store.add_texts([text], ids=[point_id(recipe.id)], metadatas=[{"recipe_id": recipe.id, "user_id": recipe.user_id}])
    logger.info("Saved document with point id:%s", id)


#def retrieve_similar_texts(query: str):
#    """Retrieve similar texts from Qdrant based on the query."""
#    logger.info("Retrieving similar texts with: %s", query[:20])
#    return vector_store.similarity_search(query, k=TOP_K)

def retrieve_similar_texts_by_user(user_id: str, query: str):
    """Retrieve similar texts from Qdrant based on the query, restricted to the given user_id."""
    logger.info("Retrieving similar texts for user_id:%s with: %s", user_id, query[:20])
    metadata_filter = Filter(
        must=[FieldCondition(key="metadata.user_id", match=MatchValue(value=user_id))]
    )
    return vector_store.similarity_search(
        query, k=TOP_K, filter=metadata_filter, score_threshold=SCORE_THRESHOLD
    )

def delete_recipe(recipe_id: str):
    vector_store.delete(ids=[point_id(recipe_id)])
    logger.info("Deleted recipe with id:%s from vector store", recipe_id)
