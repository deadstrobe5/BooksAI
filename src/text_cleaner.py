import re
from pathlib import Path
from typing import List, Tuple
from openai import OpenAI
import os
from tqdm import tqdm
from dotenv import load_dotenv

# Unset any existing OPENAI_API_KEY
if 'OPENAI_API_KEY' in os.environ:
    del os.environ['OPENAI_API_KEY']

# Load environment variables from .env file
load_dotenv()

def extract_pages(text: str) -> List[Tuple[int, str]]:
    """Extract pages and their content from the OCR text."""
    # Split text by page markers
    page_pattern = r"={40}\n\[PÁGINA (\d+)\]\n={40}\n(.*?)(?=\n={40}|\Z)"
    pages = re.findall(page_pattern, text, re.DOTALL)
    return [(int(num), content.strip()) for num, content in pages]

def clean_page_with_model(client, text: str, page_num: int) -> str:
    """Clean a single page using a language model."""
    if not text.strip():
        return f"{'='*40}\n[PÁGINA {page_num}]\n{'='*40}\n\n(Página em branco)\n"
    
    system_prompt = """Você é um assistente especializado em corrigir texto em português europeu (PT-PT) extraído por OCR.

Regras OBRIGATÓRIAS:
1. REMOVA SEMPRE o título/cabeçalho "Os princípios constitucionais estruturantes da República Portuguesa" que aparece no início da maioria das páginas. Este é apenas um cabeçalho do livro, não faz parte do texto principal.
2. REMOVA COMPLETAMENTE sequências de caracteres sem sentido, como "i ora I lums / é 2ê)" ou "rrenan, em ão) ami BB) SM) 38) EL GH)"
3. Se uma linha contém apenas caracteres aleatórios ou texto sem sentido, REMOVA-A COMPLETAMENTE
4. Corrija erros óbvios de OCR mantendo o significado original
5. Preserve a formatação de parágrafos e indentação
6. Mantenha o texto em português europeu (PT-PT)
7. Não adicione novo conteúdo substantivo
8. Preserve caracteres especiais do português (ç, á, à, â, ã, é, ê, í, ó, ô, õ, ú)
9. REMOVA TOTALMENTE artefatos de OCR como "porre ementa ombros tr mam" ou "poem me A i Aumrete terms"
10. Mantenha títulos, subtítulos e estrutura do texto, EXCETO o cabeçalho repetitivo do livro
11. Se uma página estiver vazia ou completamente ilegível, substitua por "(Página em branco)" ou "(Página ilegível)"
12. Preserve números de página e referências bibliográficas
13. ELIMINE linhas de texto sem significado como "foud 68 100"
14. REMOVA símbolos estranhos e sequências de caracteres repetidos como "tol 120 tam"
15. Sempre que encontrar texto sem coerência, REMOVA-O completamente
16. Se uma frase está incompleta no final da página, termine com "[continua]" para indicar continuação
17. Se uma frase no início da página parece continuar de uma página anterior, comece com "[continuação]"

Mantenha APENAS texto que faça sentido e tenha significado claro. É melhor remover texto duvidoso do que manter conteúdo sem sentido."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Corrija o seguinte texto da página {page_num}. REMOVA o cabeçalho repetitivo 'Os princípios constitucionais estruturantes da República Portuguesa' e todo texto sem sentido. Indique claramente continuações de frases entre páginas:\n\n{text}"}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        cleaned_text = response.choices[0].message.content.strip()
        return f"{'='*40}\n[PÁGINA {page_num}]\n{'='*40}\n\n{cleaned_text}\n"
    except Exception as e:
        print(f"Erro ao processar página {page_num}: {str(e)}")
        return f"{'='*40}\n[PÁGINA {page_num}]\n{'='*40}\n\n{text}\n"

def clean_ocr_text(input_file: str, output_file: str = None) -> None:
    """Clean OCR text using a language model while preserving page structure."""
    print(f"Lendo arquivo: {input_file}")
    
    # Verificar API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")
    
    # Inicializar cliente OpenAI com a API key do .env
    client = OpenAI(api_key=api_key)
    
    # Ler arquivo
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Extrair páginas
    pages = extract_pages(text)
    print(f"Encontradas {len(pages)} páginas")
    
    # Processar cada página
    cleaned_pages = []
    for page_num, content in tqdm(pages, desc="Limpando páginas"):
        cleaned_content = clean_page_with_model(client, content, page_num)
        cleaned_pages.append(cleaned_content)
        
        # Salvar progresso a cada 10 páginas
        if page_num % 10 == 0 or page_num == len(pages):
            temp_text = '\n'.join(cleaned_pages)
            temp_file = input_file.replace('.txt', f'_cleaned_temp.txt')
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(temp_text)
            print(f"\nProgresso salvo até a página {page_num}")
    
    # Juntar páginas limpas
    final_text = '\n'.join(cleaned_pages)
    
    # Determinar arquivo de saída
    if output_file is None:
        input_path = Path(input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_cleaned{input_path.suffix}")
    
    # Salvar resultado
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    print(f"\nTexto limpo salvo em: {output_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python text_cleaner.py <arquivo_txt>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not Path(input_file).exists():
        print(f"Erro: Arquivo {input_file} não encontrado")
        sys.exit(1)
    
    clean_ocr_text(input_file) 