import os
import sys

# Add src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vectordb.vector_store import VectorStore
from utils.config import load_config

class ChatBot:
    def __init__(self):
        # Load configuration
        config = load_config()
        
        # Initialize vector store
        self.vector_store = VectorStore(
            collection_name="law_books",
            host=config["QDRANT_HOST"],
            api_key=config["QDRANT_API_KEY"]
        )
        
        # Initialize OpenAI client
        self.openai_key = config["OPENAI_API_KEY"]
        self.context = []
    
    def search_context(self, query: str, num_results: int = 5):
        """Search for relevant context in vector store."""
        return self.vector_store.search(query, limit=num_results)
    
    def get_response(self, query: str) -> str:
        """Get response from GPT based on query and context."""
        # Search for relevant context
        context = self.search_context(query)
        
        # Format prompt with context
        prompt = f"""Com base no seguinte contexto, responda à pergunta em português europeu.
        Se a resposta não puder ser encontrada no contexto, diga que não tem informação suficiente.
        
        Contexto:
        {context}
        
        Pergunta: {query}
        
        Resposta:"""
        
        # Get response from OpenAI
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content

def main():
    chatbot = ChatBot()
    
    print("Bem-vindo ao sistema de consulta jurídica!")
    print("Digite 'sair' para terminar.")
    
    while True:
        query = input("\nSua pergunta: ").strip()
        
        if query.lower() == 'sair':
            break
        
        try:
            response = chatbot.get_response(query)
            print("\nResposta:", response)
        except Exception as e:
            print(f"\nErro ao processar pergunta: {e}")

if __name__ == "__main__":
    main() 