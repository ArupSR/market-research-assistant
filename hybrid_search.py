# hybrid_search.py
from bm25_search import rank_documents, update_bm25_corpus
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Initialize Pinecone vector store safely
try:
    index_name = "market-research"
    vector_db = PineconeVectorStore(index_name=index_name, embedding=OpenAIEmbeddings())
except Exception as e:
    print(f"⚠️ Warning: Failed to initialize Pinecone - {e}")
    vector_db = None  # Prevent crashes

def hybrid_search(query: str, top_k: int = 5) -> dict:
    """Combine BM25 and Vector Search results with error handling and improved ranking."""
    
    try:
        # ✅ Get BM25 results
        bm25_results = rank_documents(query, top_k=top_k)
    except Exception as e:
        print(f"⚠️ BM25 Error: {e}")
        bm25_results = []

    try:
        # ✅ Get Pinecone vector search results
        vector_results = []
        if vector_db:
            vector_results = [doc.page_content for doc in vector_db.similarity_search(query, k=top_k)]
    except Exception as e:
        print(f"⚠️ Pinecone Error: {e}")
        vector_results = []

    # ✅ Merge results with weighted scoring
    combined_results = bm25_results + vector_results
    ranked_results = list(dict.fromkeys(combined_results))[:top_k]  # Remove duplicates, maintain order

    return {"hybrid_results": ranked_results}

# ✅ Debugging: Test with a sample query
if __name__ == "__main__":
    test_documents = [
        "AI is transforming the finance industry",
        "Cloud computing enables scalable applications",
        "Market research AI enhances business intelligence"
    ]
    
    update_bm25_corpus(test_documents)  # ✅ Ensure BM25 has indexed documents

    test_query = "AI in finance"
    print(f"Hybrid search results for '{test_query}':", hybrid_search(test_query))
