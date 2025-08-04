from src.text_cleaner import clean_ocr_text
import sys
from pathlib import Path

def extract_first_pages(input_file: str, num_pages: int = 10) -> str:
    """Extract first N pages from the OCR text file."""
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Find all page markers
    page_markers = []
    current_pos = 0
    for i in range(num_pages + 1):  # +1 to get the start of the next page as boundary
        marker_start = text.find('='*40 + '\n[PÁGINA', current_pos)
        if marker_start == -1:
            break
        page_markers.append(marker_start)
        current_pos = marker_start + 1
    
    if len(page_markers) < 2:
        return text
    
    # Extract text up to the start of page after num_pages
    end_pos = page_markers[min(num_pages, len(page_markers)-1)]
    extracted_text = text[:end_pos]
    
    # Save to temporary file
    temp_file = input_file.replace('.txt', f'_first_{num_pages}pages.txt')
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(extracted_text)
    
    return temp_file

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python test_clean.py <arquivo_txt>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not Path(input_file).exists():
        print(f"Erro: Arquivo {input_file} não encontrado")
        sys.exit(1)
    
    # Extract first 10 pages
    temp_file = extract_first_pages(input_file, 10)
    print(f"Arquivo temporário criado: {temp_file}")
    
    # Clean the extracted pages
    clean_ocr_text(temp_file)
    print("\nProcesso de limpeza concluído!") 