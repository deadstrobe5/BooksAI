from pathlib import Path
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
from openai import OpenAI

# Unset any existing OPENAI_API_KEY
if 'OPENAI_API_KEY' in os.environ:
    del os.environ['OPENAI_API_KEY']

# Load environment variables from .env file
load_dotenv()

# Get API key from .env
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")

# Create a single OpenAI client instance with explicit API key
openai_client = OpenAI(api_key=api_key)

class BookQA:
    def __init__(self, stores_dir: str = "stores"):
        """Initialize with path to stores directory."""
        self.stores_dir = Path(stores_dir)
        
        # Create embeddings with the shared API key
        self.embeddings = OpenAIEmbeddings(
            api_key=api_key,
            model="text-embedding-3-small"  # Using the latest embedding model
        )
        
        self.available_books = self._get_available_books()
        self.active_stores = {}
    
    def _get_available_books(self) -> List[str]:
        """Get list of available book stores."""
        return [d.name for d in self.stores_dir.iterdir() if d.is_dir()]
    
    def load_books(self, book_names: Optional[List[str]] = None) -> None:
        """Load specific books or all available books if none specified."""
        # Clear current stores
        self.active_stores = {}
        
        # If no books specified, load all
        if book_names is None:
            book_names = self.available_books
        
        # Load each specified book
        for book in book_names:
            if book not in self.available_books:
                print(f"Aviso: Livro '{book}' não encontrado")
                continue
            
            store_path = self.stores_dir / book
            self.active_stores[book] = Chroma(
                persist_directory=str(store_path),
                embedding_function=self.embeddings
            )
            print(f"Carregado: {book}")
    
    def search(self, query: str, k: int = 4) -> List[dict]:
        """Search across all loaded books."""
        if not self.active_stores:
            raise ValueError("Nenhum livro carregado. Use load_books() primeiro.")
        
        results = []
        for book_name, store in self.active_stores.items():
            docs = store.similarity_search_with_score(query, k=k)
            for doc, score in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score,
                    "book": book_name
                })
        
        # Sort by score (lower is better)
        results.sort(key=lambda x: x["score"])
        return results

    def list_available_books(self) -> None:
        """Print list of available books."""
        print("\nLivros disponíveis:")
        for book in self.available_books:
            print(f"- {book}")
    
    def list_loaded_books(self) -> None:
        """Print list of currently loaded books."""
        print("\nLivros carregados:")
        if not self.active_stores:
            print("Nenhum livro carregado")
        else:
            for book in self.active_stores:
                print(f"- {book}")

if __name__ == "__main__":
    # Example usage
    qa = BookQA()
    
    print("\n=== Sistema de Consulta a Livros ===")
    qa.list_available_books()
    
    # Load all books
    print("\nCarregando todos os livros...")
    qa.load_books()
    
    while True:
        print("\nOpções:")
        print("1. Listar livros disponíveis")
        print("2. Listar livros carregados")
        print("3. Carregar livros específicos")
        print("4. Fazer uma consulta")
        print("5. Sair")
        
        choice = input("\nEscolha uma opção (1-5): ")
        
        if choice == "1":
            qa.list_available_books()
        
        elif choice == "2":
            qa.list_loaded_books()
        
        elif choice == "3":
            qa.list_available_books()
            books = input("\nDigite os nomes dos livros separados por vírgula: ").split(",")
            books = [b.strip() for b in books]
            qa.load_books(books)
        
        elif choice == "4":
            query = input("\nDigite sua consulta: ")
            k = int(input("Quantos resultados por livro (default 4): ") or "4")
            results = qa.search(query, k=k)
            
            print("\nResultados encontrados:")
            for i, r in enumerate(results, 1):
                print(f"\n--- Resultado {i} ---")
                print(f"Livro: {r['book']}")
                print(f"Página: {r['metadata']['page']}")
                print(f"Score: {r['score']:.4f}")
                print("\nConteúdo:")
                print(r['content'])
        
        elif choice == "5":
            print("\nEncerrando...")
            break
        
        else:
            print("\nOpção inválida!") 