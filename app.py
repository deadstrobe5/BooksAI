import streamlit as st
from src.book_qa import BookQA, openai_client
import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv

# Modelo padrão fixo
DEFAULT_MODEL = "gpt-4o-mini"

# Unset any existing OPENAI_API_KEY
if 'OPENAI_API_KEY' in os.environ:
    del os.environ['OPENAI_API_KEY']

# Load environment variables from .env file
load_dotenv()

# Função para busca de texto exato nos chunks
def busca_texto_exato(query, book_name="principios", max_results=3):
    chunks_file = Path(f"stores/{book_name}/chunks.json")
    if not chunks_file.exists():
        return []
    
    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    
    # Criar expressão regular para busca exata (case insensitive)
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    
    # Encontrar matches diretos
    resultados = []
    for chunk in chunks:
        # Corrigido: usando "content" em vez de "text"
        if pattern.search(chunk["content"]):
            resultados.append({
                "content": chunk["content"],
                "metadata": chunk["metadata"],
                "score": 0.0,  # Score 0 para resultados exatos (melhor prioridade)
                "book": book_name,
                "match_tipo": "exato"
            })
            if len(resultados) >= max_results:
                break
    
    return resultados

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'qa' not in st.session_state:
    st.session_state.qa = BookQA()
    # Carregar apenas o livro "principios"
    st.session_state.qa.load_books(["principios"])

def get_gpt_response(query: str, context: str) -> str:
    """Get response from GPT model."""
    system_prompt = """Você é um assistente especializado em direito constitucional português.
    Use o contexto fornecido para responder à pergunta do utilizador.
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
    
    # Get response
    response = openai_client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=0
    )
    
    return response.choices[0].message.content

# App title and styling
st.set_page_config(page_title="Consulta de Livros Jurídicos", layout="wide", page_icon="📚")

# App title
st.title("📚 Consulta de Livros Jurídicos")
st.caption("Os princípios constitucionais estruturantes da República Portuguesa - Jorge Reis Novais")

# Sidebar for book selection
st.sidebar.title("Configurações")

# Show model information
st.sidebar.write(f"### Modelo: {DEFAULT_MODEL}")

# Number of chunks slider
num_chunks = st.sidebar.slider(
    "Número de páginas a recuperar:",
    min_value=2,
    max_value=10,
    value=4,
    step=1,
    help="Quantidade de páginas que serão buscadas nos livros"
)

# Opção para ativar busca híbrida
usar_busca_hibrida = st.sidebar.checkbox("Usar busca híbrida (recomendado para datas e termos exatos)", value=True)

# Main chat interface
st.write("### Chat")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if query := st.chat_input("Digite sua pergunta..."):
    # Add user message to chat
    st.session_state.chat_history.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)
    
    # Search for relevant chunks
    with st.spinner("Buscando informações relevantes..."):
        # Busca híbrida: combine busca exata com busca vetorial
        results = []
        
        if usar_busca_hibrida:
            # Primeiro tenta busca exata
            exact_results = busca_texto_exato(query, "principios")
            if exact_results:
                st.sidebar.success(f"Encontradas {len(exact_results)} correspondências exatas!")
                results.extend(exact_results)
        
        # Adiciona resultados da busca vetorial
        vector_results = st.session_state.qa.search(query, k=num_chunks)
        
        # Filtrar para evitar duplicações de páginas
        seen_pages = set(r["metadata"]["page"] for r in results)
        filtered_vector_results = []
        
        for r in vector_results:
            if r["metadata"]["page"] not in seen_pages:
                seen_pages.add(r["metadata"]["page"])
                r["match_tipo"] = "vetorial"
                filtered_vector_results.append(r)
        
        results.extend(filtered_vector_results)
        
        # Ordenar por score (menor é melhor)
        results = sorted(results, key=lambda x: x["score"])
        
        # Limitar ao número solicitado
        if len(results) > num_chunks:
            results = results[:num_chunks]
    
    # Prepare context
    context = "\n\n".join([
        f"[Página {r['metadata']['page']}]\n{r['content']}"
        for r in results
    ])
    
    # Get GPT response
    with st.spinner(f"Gerando resposta com {DEFAULT_MODEL}..."):
        response = get_gpt_response(query, context)
    
    # Add assistant message to chat
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response
    })
    with st.chat_message("assistant"):
        st.write(response)
    
    # Show sources
    with st.expander("Ver fontes utilizadas"):
        for i, r in enumerate(results, 1):
            match_type = "📍 Match Exato" if r.get("match_tipo") == "exato" else "🔍 Match Vetorial"
            st.subheader(f"Fonte {i} - {match_type} (Relevância: {r['score']:.4f})")
            st.caption(f"Página {r['metadata']['page']}")
            st.text_area("Conteúdo", r['content'], height=200, key=f"source_{i}") 