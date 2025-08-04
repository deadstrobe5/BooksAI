from src.pdf_processor import process_pdf_ocr
import sys
from pathlib import Path

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ocr_book.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not Path(pdf_path).exists():
        print(f"Error: File {pdf_path} not found")
        sys.exit(1)
    
    process_pdf_ocr(pdf_path)
    print("\nDone! The text file was saved with the same name as the PDF but with .txt extension.") 