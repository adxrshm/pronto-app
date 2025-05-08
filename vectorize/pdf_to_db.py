import os
import re
import sys
from typing import List, Dict
import pandas as pd
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from tqdm import tqdm
import time
from langsmith import traceable
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_pinecone(api_key):
    """Initialize Pinecone client"""
    if not api_key:
        raise ValueError("Pinecone API key is not set. Please check your .env file.")
    
    print("Initializing Pinecone client...")
    pc = Pinecone(api_key=api_key)
    return pc

def init_openai(api_key):
    """Initialize OpenAI client"""
    if not api_key:
        raise ValueError("OpenAI API key is not set. Please check your .env file.")
        
    print("Initializing OpenAI client...")
    return OpenAI(api_key=api_key)

def clean_heading(text: str) -> str:
    """Remove markdown heading symbols and clean the text"""
    return re.sub(r'^#+\s*', '', text.strip())

def split_by_headings(markdown_text: str) -> List[Dict[str, str]]:
    """
    Split markdown text into sections based on headings.
    Returns a list of dictionaries containing heading and content.
    """
    # Split the text into lines
    lines = markdown_text.strip().split('\n')
    sections = []
    current_heading = "Root"
    current_content = []
    
    for line in lines:
        # Check if line is a heading
        if line.strip().startswith('#'):
            # Save the previous section if it exists
            if current_content:
                sections.append({
                    'heading': clean_heading(current_heading),
                    'content': '\n'.join(current_content).strip()
                })
            current_heading = line
            current_content = []
        else:
            current_content.append(line)
    
    # Add the last section
    if current_content:
        sections.append({
            'heading': clean_heading(current_heading),
            'content': '\n'.join(current_content).strip()
        })
    
    return sections

def recursive_split(text: str, max_length: int = 1000) -> List[str]:
    """
    Recursively split text into smaller chunks while preserving context.
    """
    if len(text) <= max_length:
        return [text]
    
    # Try to split at paragraph breaks first
    paragraphs = text.split('\n\n')
    if len(paragraphs) > 1:
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            if current_length + len(para) > max_length and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_length = 0
            current_chunk.append(para)
            current_length += len(para) + 2  # +2 for '\n\n'
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        return chunks
    
    # If no paragraph breaks, split at sentence level
    split_point = text.rfind('. ', 0, max_length)
    if split_point == -1:
        split_point = max_length
    
    return [text[:split_point]] + recursive_split(text[split_point:].strip(), max_length)

@traceable(run_type="llm")
def get_embedding(text, client):
    """Get embedding from OpenAI API with LangSmith tracking"""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

def verify_pinecone_connection(pc, index_name):
    """Verify Pinecone connection and index existence"""
    try:
        # Check if we can list indexes (basic connection test)
        indexes = pc.list_indexes().names()
        print(f"Successfully connected to Pinecone. Available indexes: {indexes}")
        
        # Check if index exists
        if index_name in indexes:
            print(f"Index '{index_name}' exists.")
            # Test query to verify access
            index = pc.Index(index_name)
            try:
                stats = index.describe_index_stats()
                print(f"Index stats: {stats}")
                return True
            except Exception as e:
                print(f"Error accessing index: {e}")
                return False
        else:
            print(f"Index '{index_name}' doesn't exist yet. Will create it during processing.")
            return True
    except Exception as e:
        print(f"Error connecting to Pinecone: {e}")
        return False

@traceable(run_type="chain")
def process_markdown_files(markdown_folder: str, index_name: str, pc, openai_client, batch_size=100):
    """Process all Markdown files in the folder and upload to Pinecone"""
    # Check if folder exists
    if not os.path.exists(markdown_folder):
        raise FileNotFoundError(f"Markdown folder not found: {markdown_folder}")
    
    # Verify Pinecone connection
    if not verify_pinecone_connection(pc, index_name):
        raise ConnectionError("Cannot proceed due to Pinecone connection issues")
    
    cloud = os.environ.get('PINECONE_CLOUD') or 'aws'
    region = os.environ.get('PINECONE_REGION') or 'us-east-1'
    print(f"Using Pinecone cloud: {cloud}, region: {region}")
    spec = ServerlessSpec(cloud=cloud, region=region)
    
    try:
        # Create Pinecone index if it doesn't exist
        if index_name not in pc.list_indexes().names():
            print(f"Creating index '{index_name}'...")
            pc.create_index(
                spec=spec,
                name=index_name,
                dimension=1536,
                metric='cosine'
            )
            print(f"Index '{index_name}' created successfully!")
            # Wait for index to initialize
            print("Waiting for index to initialize...")
            time.sleep(30)
        
        # Get index
        print(f"Connecting to index '{index_name}'...")
        index = pc.Index(index_name)
        total_processed = 0
        total_errors = 0
        
        # List all markdown files
        md_files = [f for f in os.listdir(markdown_folder) if f.endswith(('.md', '.markdown'))]
        if not md_files:
            print(f"No markdown files found in {markdown_folder}")
            return {"total_processed": 0, "total_errors": 0}
        
        print(f"Found {len(md_files)} markdown files to process")
        
        # Process each Markdown file
        for filename in md_files:
            print(f"Processing {filename}")
            file_path = os.path.join(markdown_folder, filename)
            
            # Read Markdown file
            with open(file_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Split into sections by headings
            sections = split_by_headings(markdown_content)
            print(f"Split {filename} into {len(sections)} sections")
            
            # Prepare batches for upload
            vectors = []
            file_processed = 0
            file_errors = 0
            
            # Process each section
            for section_idx, section in enumerate(tqdm(sections, desc="Processing sections")):
                # Split content into smaller chunks if needed
                chunks = recursive_split(section['content'])
                
                for chunk_idx, chunk in enumerate(chunks):
                    # Skip empty chunks
                    if not chunk.strip():
                        continue
                    
                    # Get embedding
                    embedding = get_embedding(chunk, openai_client)
                    if embedding:
                        try:
                            vectors.append((
                                f"{filename}-{section_idx}-{chunk_idx}",  # ID
                                embedding,
                                {
                                    "heading": section['heading'],
                                    "text": chunk[:3600],  # Limiting text length for Pinecone
                                    "filename": filename
                                }
                            ))
                            file_processed += 1
                        except Exception as e:
                            print(f"Error creating vector entry: {e}")
                            file_errors += 1
                    else:
                        file_errors += 1
                    
                    # Upload batch if ready
                    if len(vectors) >= batch_size:
                        try:
                            print(f"Uploading batch of {len(vectors)} vectors...")
                            index.upsert(vectors=vectors)
                            vectors = []
                            print("Batch uploaded successfully!")
                            time.sleep(1)  # Rate limiting
                        except Exception as e:
                            print(f"Error uploading batch: {e}")
                            # Retry with smaller batches
                            if len(vectors) > 10:
                                print("Retrying with smaller batch size...")
                                half_size = len(vectors) // 2
                                try:
                                    index.upsert(vectors=vectors[:half_size])
                                    time.sleep(1)
                                    index.upsert(vectors=vectors[half_size:])
                                    vectors = []
                                    print("Smaller batches uploaded successfully!")
                                except Exception as e2:
                                    print(f"Error uploading smaller batches: {e2}")
                                    file_errors += len(vectors)
                                    vectors = []
                            else:
                                file_errors += len(vectors)
                                vectors = []
            
            # Upload remaining vectors
            if vectors:
                try:
                    print(f"Uploading final batch of {len(vectors)} vectors...")
                    index.upsert(vectors=vectors)
                    print("Final batch uploaded successfully!")
                except Exception as e:
                    print(f"Error uploading final batch: {e}")
                    file_errors += len(vectors)
            
            total_processed += file_processed
            total_errors += file_errors
            print(f"Processed {file_processed} chunks with {file_errors} errors from {filename}")
        
        print(f"Total processed: {total_processed} chunks with {total_errors} errors")
        return {
            "total_processed": total_processed,
            "total_errors": total_errors
        }
    except Exception as e:
        print(f"Error in processing: {e}")
        raise e

def main():
    # Configuration
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    INDEX_NAME = os.getenv("PINECONE_INDEX_NAME") or "markdown-embeddings"
    MARKDOWN_FOLDER = os.getenv("MARKDOWN_FOLDER") or "output_pdf"
    
    # Print configuration (without sensitive keys)
    print("Configuration:")
    print(f"  INDEX_NAME: {INDEX_NAME}")
    print(f"  MARKDOWN_FOLDER: {MARKDOWN_FOLDER}")
    print(f"  PINECONE_API_KEY: {'Set' if PINECONE_API_KEY else 'Not set'}")
    print(f"  OPENAI_API_KEY: {'Set' if OPENAI_API_KEY else 'Not set'}")
    
    # Initialize clients
    try:
        pc = init_pinecone(PINECONE_API_KEY)
        openai_client = init_openai(OPENAI_API_KEY)
        
        # Process files
        process_markdown_files(MARKDOWN_FOLDER, INDEX_NAME, pc, openai_client)
        print("Processing completed successfully!")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()