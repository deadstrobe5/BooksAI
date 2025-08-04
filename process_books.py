from pathlib import Path
from src.text_chunker import process_book

def main():
    # Find all cleaned text files
    data_dir = Path("data")
    cleaned_files = list(data_dir.glob("*_cleaned.txt"))
    
    if not cleaned_files:
        print("Nenhum arquivo de texto limpo encontrado em data/")
        return
    
    print(f"Encontrados {len(cleaned_files)} arquivos para processar:")
    for f in cleaned_files:
        print(f"- {f.name}")
    
    print("\nProcessando arquivos...")
    for f in cleaned_files:
        print(f"\nProcessando {f.name}...")
        process_book(str(f))
    
    print("\nProcessamento concluído!")

if __name__ == "__main__":
    main() 