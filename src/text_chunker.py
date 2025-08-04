import re
from pathlib import Path
from typing import List, Dict, Any
import json
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import TextSplitter
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Unset any existing OPENAI_API_KEY
if 'OPENAI_API_KEY' in os.environ:
    del os.environ['OPENAI_API_KEY']

# Load environment variables from .env file
load_dotenv()

# Get API key from .env
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")

class PageChunker:
    def __init__(self, cleaned_text_file: str):
        """Initialize with path to cleaned text file."""
        self.text_file = cleaned_text_file
        self.book_name = Path(cleaned_text_file).stem.replace('_cleaned', '')
    
    def extract_pages(self) -> List[Dict[str, Any]]:
        """Extract pages from cleaned text, returning list of dicts with content and metadata."""
        with open(self.text_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Find all page markers and their content
        page_pattern = r"={40}\n\[PÁGINA (\d+)\]\n={40}\n(.*?)(?=\n={40}|\Z)"
        pages = re.findall(page_pattern, text, re.DOTALL)
        
        chunks = []
        for page_num, content in pages:
            content = content.strip()
            # Skip empty pages or pages marked as blank
            if not content or content == "(Página em branco)" or content == "(Página ilegível)":
                continue
            
            chunks.append({
                "content": content,
                "metadata": {
                    "page": int(page_num),
                    "book": self.book_name,
                    "source": Path(self.text_file).name
                }
            })
        
        return chunks

def create_book_store(chunks: List[Dict[str, Any]], store_dir: str) -> None:
    """Create a vector store for a book's chunks."""
    # Create embeddings using the global API key
    embeddings = OpenAIEmbeddings(
        api_key=api_key,
        model="text-embedding-3-small"  # Using the latest embedding model
    )
    
    # Create vector store
    texts = [chunk["content"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    
    Chroma.from_texts(
        texts=texts,
        metadatas=metadatas,
        embedding=embeddings,
        persist_directory=store_dir
    )

def process_book(cleaned_text_file: str, output_dir: str = "stores") -> None:
    """Process a cleaned book text file into chunks and create its vector store."""
    # Create chunker
    chunker = PageChunker(cleaned_text_file)
    
    # Extract pages
    print(f"Extraindo páginas de {chunker.book_name}...")
    chunks = chunker.extract_pages()
    print(f"Encontrados {len(chunks)} chunks válidos")
    
    # Create store directory
    store_dir = Path(output_dir) / chunker.book_name
    store_dir.mkdir(parents=True, exist_ok=True)
    
    # Save chunks to JSON for reference
    chunks_file = store_dir / "chunks.json"
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"Chunks salvos em {chunks_file}")
    
    # Create vector store
    print("Criando vector store...")
    create_book_store(chunks, str(store_dir))
    print(f"Vector store criada em {store_dir}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python text_chunker.py <arquivo_texto_limpo>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not Path(input_file).exists():
        print(f"Erro: Arquivo {input_file} não encontrado")
        sys.exit(1)
    
    process_book(input_file) 