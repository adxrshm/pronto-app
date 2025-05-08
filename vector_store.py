# vector_store.py
import os
from typing import List, Dict, Any
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Set up logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "markdown")


@tool
def query_vector_store(
    query: str,
    top_k: int = 5,
    threshold: float = 0.7,
) -> List[Dict[str, Any]]:
    """
    Query the vector store and return a list of relevant text passages.
 "pinecone[asyncio,grpc]"
    Args:
        query (str): The user's search query
        top_k (int, optional): Number of results to return. Defaults to 5.
        threshold (float, optional): Minimum similarity score to include. Defaults to 0.7.

    Returns:
        List[Dict[str, Any]]: List of relevant text passages with metadata and scores
    """
    try:
        logger.info(f"Querying vector store with: {query}")
        
        # Initialize embeddings model
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=OPENAI_API_KEY,
        )
        
        # Connect to Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        
        # Generate query embedding
        query_embedding = embeddings.embed_query(query)
        print(query_embedding)
        
        # Query Pinecone
        results = index.query(
            vector=query_embedding, 
            top_k=top_k, 
            include_metadata=True,
            threshold=0.2
           # We don't need the vector values themselves
        )
        
        # Process results
        relevant_results = []
        
        if len(relevant_results)>0:
            print(f"type of matches is {type( relevant_results[0])}")
        relevant_texts = [match.metadata["text"] for match in results.matches]
        return relevant_texts
        # for match in results.matches:
        #     # Only include results above similarity threshold
        #     if match.score >= threshold:
        #         relevant_results.append({
        #             "text": match.metadata.get("text", ""),
        #             "score": match.score,
        #             "metadata": {k: v for k, v in match.metadata.items() if k != "text"}
        #         })
        
        # logger.info(f"Found {len(relevant_results)} relevant results above threshold {threshold}")
        # return relevant_results

    except Exception as e:
        logger.exception(f"Error during vector store query: {e!r}")
        return []


