import os
from pdf2image import convert_from_path
import pytesseract
import re
from PIL import Image, ImageEnhance
from pathlib import Path

def preprocess_image(image):
    """Preprocess image to improve OCR quality."""
    # Convert to grayscale if not already
    if image.mode != 'L':
        image = image.convert('L')
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)
    
    return image

def clean_text(text: str) -> str:
    """Clean OCR artifacts and normalize text."""
    # Remove non-printable characters except newlines
    text = ''.join(char for char in text if char.isprintable() or char in '\n')
    
    # Fix common OCR errors
    text = text.replace('|', 'I')
    text = re.sub(r'(?<=[a-z])\.(?=[A-Z])', '. ', text)  # Add space after period
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # Add space between words
    
    # Fix broken words at line endings
    text = re.sub(r'-\s+([a-z])', r'\1', text)
    text = re.sub(r'([a-z])-\s+([a-z])', r'\1\2', text)
    
    # Fix Portuguese specific characters
    replacements = {
        r'\bao\b': 'ão',
        r'\bcao\b': 'ção',
        r'\boes\b': 'ões',
        r'\bnao\b': 'não',
        r'\bsao\b': 'são',
        r'\besta\b': 'está',
        r'\bate\b': 'até',
        r'\be\s': 'é ',
        r'\bja\b': 'já',
        r'\bha\b': 'há',
        'RÉ S': 'REIS',
        'PÉ SOA': 'PESSOA',
        'DIRÉ TO': 'DIREITO',
        'FUNDAMÉ TAIS': 'FUNDAMENTAIS'
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Remove excessive whitespace but keep paragraph structure
    lines = text.split('\n')
    cleaned_lines = []
    current_paragraph = []
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_paragraph:
                cleaned_lines.append(' '.join(current_paragraph))
                current_paragraph = []
            continue
        
        # If line ends with sentence-ending punctuation, it's end of paragraph
        if line[-1] in '.!?':
            current_paragraph.append(line)
            cleaned_lines.append(' '.join(current_paragraph))
            current_paragraph = []
        else:
            current_paragraph.append(line)
    
    # Don't forget last paragraph
    if current_paragraph:
        cleaned_lines.append(' '.join(current_paragraph))
    
    return '\n\n'.join(cleaned_lines)

def process_pdf_ocr(pdf_path: str, output_path: str = None) -> None:
    """Process a PDF file with OCR and save the text with page markers."""
    print(f"Processing: {pdf_path}")
    
    # Convert PDF to images
    print("Converting PDF to images...")
    pages = convert_from_path(pdf_path, dpi=300)
    
    # Process each page
    all_text = []
    for i, page in enumerate(pages, 1):
        print(f"Processing page {i}...")
        
        # Preprocess image
        processed_page = preprocess_image(page)
        
        # Extract text with OCR
        page_text = pytesseract.image_to_string(processed_page, lang='por')
        
        # Clean text
        cleaned_text = clean_text(page_text)
        
        # Add page marker
        page_marker = f"\n{'='*40}\n[PÁGINA {i}]\n{'='*40}\n"
        all_text.append(f"{page_marker}\n{cleaned_text}")
    
    # Join all pages
    final_text = '\n\n'.join(all_text)
    
    # Determine output path
    if output_path is None:
        output_path = str(Path(pdf_path).with_suffix('.txt'))
    
    # Save text
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    print(f"\nProcessed text saved to: {output_path}")

if __name__ == "__main__":
    # Process the dignity book as an example
    pdf_path = "data/JORGE-REIS-NOVAIS-a-Dignidade-Da-Pessoa-Humana.pdf"
    process_pdf_ocr(pdf_path) 