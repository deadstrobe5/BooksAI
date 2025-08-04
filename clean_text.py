from src.text_cleaner import clean_ocr_text
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Unset any existing OPENAI_API_KEY
if 'OPENAI_API_KEY' in os.environ:
    del os.environ['OPENAI_API_KEY']

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python clean_text.py <arquivo_txt>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not Path(input_file).exists():
        print(f"Erro: Arquivo {input_file} não encontrado")
        sys.exit(1)
    
    clean_ocr_text(input_file)
    print("\nProcesso de limpeza concluído!") 