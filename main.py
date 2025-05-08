# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import List, Dict, Any
import logging

# Import the agent
from agent import SimplePineconeResearchAgent

# Load environment variables
load_dotenv()

# Set up logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize the agent
try:
    agent = SimplePineconeResearchAgent()
    logger.info("Agent initialized successfully!")
except Exception as e:
    logger.error(f"Failed to initialize agent: {e}")
    raise

# Create FastAPI app
app = FastAPI(title="Pinecone Research Chat API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class QueryRequest(BaseModel):
    query: str

# Define response model
class QueryResponse(BaseModel):
    response: str

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Pinecone Research Chat API is running"}

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    try:
        logger.info(f"Received query: {request.query}")
        response = agent.query(request.query)
        return {"response": response}
    except Exception as e:
        logger.exception(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI server if this script is executed directly
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)