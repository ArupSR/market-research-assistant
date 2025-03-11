import nltk
import os
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize

# ✅ Set Persistent NLTK Data Path (Recommended)
NLTK_DATA_PATH = "C:/nltk_data"  # Change this if needed
nltk.data.path.append(NLTK_DATA_PATH)

# ✅ Ensure necessary NLTK resources are available
try:
    if not os.path.exists(f"{NLTK_DATA_PATH}/tokenizers/punkt"):
        nltk.download("punkt", download_dir=NLTK_DATA_PATH)
except Exception as e:
    print(f"⚠️ Warning: NLTK resource download failed: {e}")

# ✅ Initialize BM25 with sample dataset if empty
documents = [
    "NVIDIA is a leader in AI computing and GPUs.",
    "Tesla produces electric cars and is expanding into AI and robotics.",
    "Microsoft develops cloud solutions like Azure and Office 365.",
    "Apple is known for iPhones, MacBooks, and innovative technology.",
    "Amazon dominates e-commerce and cloud computing with AWS."
]
tokenized_docs = [word_tokenize(doc.lower()) for doc in documents]
bm25 = BM25Okapi(tokenized_docs)

def update_bm25_corpus(new_documents):
    """
    Updates the BM25 document corpus dynamically.
    
    Args:
        new_documents (list): List of new documents to index.
    """
    global documents, tokenized_docs, bm25

    if not new_documents:
        print("⚠️ Warning: No documents provided for BM25 indexing.")
        return

    documents = new_documents
    tokenized_docs = [word_tokenize(doc.lower()) for doc in documents]
    bm25 = BM25Okapi(tokenized_docs)
    print(f"✅ BM25 Corpus Updated! {len(documents)} documents indexed.")

def rank_documents(query, top_k=3):
    """
    Retrieve and rank documents using BM25.

    Args:
        query (str): The search query.
        top_k (int): Number of top results to return.

    Returns:
        list: Ranked list of relevant documents.
    """
    if not query.strip():
        return ["⚠️ Error: Query cannot be empty!"]

    if not bm25 or not documents:
        return ["⚠️ Error: No indexed documents available for search."]

    tokenized_query = word_tokenize(query.lower())
    scores = bm25.get_scores(tokenized_query)

    ranked_docs = sorted(zip(scores, documents), reverse=True)
    
    return [doc for _, doc in ranked_docs[:top_k]]

# ✅ Debugging: Test with a sample query
if __name__ == "__main__":
    sample_query = "AI in finance"
    results = rank_documents(sample_query)
    print(f"🔍 Search Results for '{sample_query}':", results)
