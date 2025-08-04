#!/usr/bin/env python3
import sys
from src.book_qa import BookQA, openai_client
import os
from dotenv import load_dotenv
import time
from src.cost_calculator import count_tokens, calculate_cost, format_cost

# Modelo a ser usado
MODEL = "gpt-4o-mini"

# Unset any existing OPENAI_API_KEY
if 'OPENAI_API_KEY' in os.environ:
    del os.environ['OPENAI_API_KEY']

# Load environment variables from .env file
load_dotenv()

def get_gpt_response(query: str, context: str) -> tuple[str, float]:
    """Get response from GPT-4o-mini and calculate costs."""
    print(f"Chamando {MODEL}...")
    start = time.time()
    
    system_prompt = """Você é um assistente especializado em direito constitucional português.
    Use o contexto fornecido para responder à pergunta do usuário.
    Baseie sua resposta APENAS no contexto fornecido.
    Se o contexto não for suficiente para responder à pergunta, diga isso claramente.
    Cite as páginas relevantes do livro em sua resposta."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"""Contexto do livro:
        {context}
        
        Pergunta: {query}
        
        Por favor, responda à pergunta usando apenas o contexto fornecido acima."""}
    ]
    
    # Count input tokens
    input_text = "".join(m["content"] for m in messages)
    input_tokens = count_tokens(input_text)
    
    response = openai_client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0
    )
    
    # Get response text and count output tokens
    response_text = response.choices[0].message.content
    output_tokens = count_tokens(response_text)
    
    # Calculate cost
    cost = calculate_cost(input_tokens, output_tokens)
    
    print(f"{MODEL} respondeu em {time.time() - start:.2f} segundos")
    print(f"Tokens: {input_tokens} entrada, {output_tokens} saída")
    print(f"Custo: {format_cost(cost)}")
    
    return response_text, cost

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 query_book.py <consulta>")
        sys.exit(1)
    
    # Get query from command line arguments (handle multiple words)
    query = " ".join(sys.argv[1:])
    
    # Initialize QA system and load books
    print("Inicializando sistema...")
    start = time.time()
    qa = BookQA()
    qa.load_books()
    print(f"Sistema inicializado em {time.time() - start:.2f} segundos")
    
    # Search
    print("\nBuscando chunks relevantes...")
    start = time.time()
    results = qa.search(query, k=4)
    print(f"Chunks encontrados em {time.time() - start:.2f} segundos")
    
    # Calculate embedding cost
    embedding_tokens = count_tokens(query, model="text-embedding-3-small")
    embedding_cost = calculate_cost(embedding_tokens, 0, model="text-embedding-3-small")
    print(f"Custo dos embeddings: {format_cost(embedding_cost)}")
    
    # Prepare context from results
    context = "\n\n".join([
        f"[Página {r['metadata']['page']}]\n{r['content']}"
        for r in results
    ])
    
    # Get GPT response
    response, response_cost = get_gpt_response(query, context)
    
    # Total cost
    total_cost = response_cost + embedding_cost
    
    print("\nResposta:")
    print("=" * 80)
    print(response)
    print("=" * 80)
    print(f"Custo total: {format_cost(total_cost)}")
    
    print("\nTrechos relevantes utilizados:")
    for i, r in enumerate(results, 1):
        print(f"\n--- Trecho {i} ---")
        print(f"Livro: {r['book']}")
        print(f"Página: {r['metadata']['page']}")
        print(f"Score: {r['score']:.4f}")
        print("\nConteúdo:")
        print(r['content'])

if __name__ == "__main__":
    main() 