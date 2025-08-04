from pdf2image import convert_from_path
import pytesseract
import os
from tqdm import tqdm

def test_ocr_extraction():
    # Get all PDF files in current directory
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    
    for pdf_file in pdf_files:
        print(f"\nTesting OCR extraction from: {pdf_file}")
        print("=" * 80)
        
        # Convert PDF pages to images
        try:
            # Only convert first 10 pages
            pages = convert_from_path(pdf_file, first_page=1, last_page=10)
            
            for i, page in enumerate(tqdm(pages, desc="Processing pages")):
                print(f"\nPage {i+1}:")
                print("-" * 40)
                
                # Perform OCR on the page
                text = pytesseract.image_to_string(page, lang='por')  # Using Portuguese language
                
                # Print first 500 characters of each page as a sample
                print(text[:500])
                print(f"\nTotal characters in page: {len(text)}")
                
        except Exception as e:
            print(f"Error processing {pdf_file}: {str(e)}")

if __name__ == "__main__":
    test_ocr_extraction() 