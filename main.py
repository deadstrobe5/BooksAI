import os
from pathlib import Path

from src.pdf_processor import process_pdf, needs_ocr
from src.vector_store import VectorStore
from src.config import load_config

def process_pdfs(pdf_dir: str) -> list:
    """Process PDFs from a directory and return text chunks."""
    chunks = []
    pdf_files = list(Path(pdf_dir).glob("*.pdf"))
    
    for pdf_path in pdf_files:
        print(f"\nProcessing {pdf_path.name}...")
        
        # Check if PDF needs OCR
        requires_ocr = needs_ocr(str(pdf_path))
        print(f"OCR needed: {requires_ocr}")
        
        # Process PDF and get chunks
        doc_chunks = process_pdf(str(pdf_path), needs_ocr=requires_ocr)
        
        # Add source information to chunks
        chunks.extend([{
            "text": chunk,
            "metadata": {
                "source": pdf_path.name,
                "type": "ocr" if requires_ocr else "text"
            }
        } for chunk in doc_chunks])
        
        # Save processed text
        if doc_chunks:
            text_path = Path("data") / f"{pdf_path.stem}.txt"
            with open(text_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(doc_chunks))
    
    return chunks

def main():
    # Load configuration
    config = load_config()
    
    # Initialize vector store
    vector_store = VectorStore(
        collection_name="law_books",
        host=config["QDRANT_HOST"],
        api_key=config["QDRANT_API_KEY"]
    )
    
    # Process all PDFs
    print("\nProcessing PDFs...")
    chunks = process_pdfs("data")
    if chunks:
        vector_store.add_texts(chunks)
        print(f"Added {len(chunks)} chunks to vector store")

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    Path("data").mkdir(exist_ok=True)
    main() 