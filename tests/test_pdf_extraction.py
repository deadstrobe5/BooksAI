from pypdf import PdfReader
import os

def test_pdf_extraction():
    # Get all PDF files in current directory
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    
    for pdf_file in pdf_files:
        print(f"\nTesting extraction from: {pdf_file}")
        print("=" * 80)
        
        reader = PdfReader(pdf_file)
        
        # Test first 10 pages or all pages if less than 10
        num_pages = min(10, len(reader.pages))
        
        for i in range(num_pages):
            print(f"\nPage {i+1}:")
            print("-" * 40)
            
            text = reader.pages[i].extract_text()
            # Print first 500 characters of each page as a sample
            print(text[:500])
            print(f"\nTotal characters in page: {len(text)}")

if __name__ == "__main__":
    test_pdf_extraction() 