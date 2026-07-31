from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from database import COLLECTION_NAME, get_qdrant_client
import json
from aiokafka import AIOKafkaConsumer
import asyncio
import logging
import uuid


TOP_K = 2  # Number of similar texts to retrieve
RECIPE_CREATED_TOPIC = "recipe-created"

client = get_qdrant_client()

load_dotenv()  # Load environment variables from .env file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")  # Initialize OpenAI embeddings

vector_store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
)

def vectorize_text(text: str, recipe_id: str):
    """Generate embeddings for the given text and store them in Qdrant."""
    logger.info("Generating and storing embeddings with id:%s", recipe_id)
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, recipe_id))
    id = vector_store.add_texts([text], ids=[point_id], metadatas=[{"recipe_id": recipe_id}])
    logger.info("Saved document with id:%s", id)

def retrieve_similar_texts(query: str):
    """Retrieve similar texts from Qdrant based on the query."""
    return vector_store.similarity_search(query, k=TOP_K)

async def consume_recipe_events():
    logger.info("Starting Kafka consumer.")
    consumer = AIOKafkaConsumer(RECIPE_CREATED_TOPIC, bootstrap_servers='localhost:9092',
                    group_id="recipe-embedding-service",
                    value_deserializer=lambda v:json.loads(v.decode("utf-8")),
                    key_deserializer=lambda k: k.decode("utf-8"),
                    auto_offset_reset="earliest"
                    )
    await consumer.start()
    
    try:
        async for msg in consumer:
            key = msg.key
            recipe = msg.value
            logger.info("Consumed kafka event with key=%s and value=%s", key, recipe)
            
            combined_text = f"{recipe['name']}\n{recipe['description']}\n{', '.join(recipe['ingredients'])}\n{recipe['instructions']}"
            vectorize_text(combined_text, recipe["id"])
            
    finally:
        await consumer.stop()        

if __name__ == "__main__":
    asyncio.run(consume_recipe_events())
