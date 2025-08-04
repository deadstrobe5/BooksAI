from pdf_processor import PDFProcessor
from vector_store import VectorStore
from chat import ChatBot

def main():
    # Initialize components
    pdf_processor = PDFProcessor()
    vector_store = VectorStore()
    chatbot = ChatBot()

    # Process first 5 pages of each PDF
    print("Processing PDFs (first 5 pages)...")
    chunks = pdf_processor.process_directory(max_pages=5)
    print(f"\nTotal chunks generated: {len(chunks)}")

    # Add chunks to vector store
    print("\nAdding chunks to vector store...")
    vector_store.add_documents(chunks)

    # Test queries
    test_queries = [
        "O que é a dignidade da pessoa humana?",
        "Qual é o papel do Estado de Direito na República Portuguesa?",
        "Como se relaciona a dignidade humana com os direitos fundamentais?",
        "Quais são os princípios constitucionais estruturantes?",
        "O que significa Estado Social e Democrático de Direito?"
    ]

    print("\nTesting queries...")
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 80)
        
        # Get relevant chunks
        results = vector_store.search(query, limit=3)
        
        # Add context to chatbot
        chatbot.add_context(results)
        
        # Get response
        response = chatbot.get_response(query)
        print("\nResponse:", response)
        
        print("\nSource chunks:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. From {result['source']} (score: {result['score']:.3f}):")
            print(result['text'][:200] + "...")

if __name__ == "__main__":
    main() 