import os
from dotenv import load_dotenv

def load_config():
    """Load configuration from environment variables."""
    # Load .env file from project root
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    load_dotenv(env_path)
    
    # Required environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "QDRANT_HOST",
        "QDRANT_API_KEY"
    ]
    
    # Check for missing environment variables
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Return configuration dictionary
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "QDRANT_HOST": os.getenv("QDRANT_HOST"),
        "QDRANT_API_KEY": os.getenv("QDRANT_API_KEY"),
        "CHAT_MODEL": os.getenv("CHAT_MODEL", "gpt-4"),  # Default to GPT-4
        "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),  # Default to latest embedding model
        "CHUNK_SIZE": int(os.getenv("CHUNK_SIZE", "2000")),  # Default chunk size
        "CHUNK_OVERLAP": int(os.getenv("CHUNK_OVERLAP", "400")),  # Default chunk overlap
    }

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4-turbo-preview"

# Qdrant settings
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "books"

# Chunking settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# File settings
PDF_DIR = "."  # Current directory where PDFs are stored 