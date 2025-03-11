from fastapi import FastAPI
import spacy
import openai
import os
import pinecone
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore  # ✅ Corrected Import
from langchain_openai import OpenAIEmbeddings
from bm25_search import rank_documents  # ✅ Import BM25 function
from nanny_filter import compliance_filter  # ✅ Import compliance filtering from nanny.py
from live_feed import get_live_news # ✅ Import get_live_news from live_feed.py
from yahoo_finance import get_stock_data
from google_trends import get_google_trends


# ✅ Load environment variables
load_dotenv()

# ✅ Load API Keys
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("❌ ERROR: Pinecone API Key is missing. Add it to .env file.")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: OpenAI API Key is missing. Add it to .env file.")

# ✅ Initialize Pinecone
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)

# ✅ Define Index
index_name = "market-research"

# ✅ Check if Index Exists, Else Create It
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
    )
    print(f"✅ Created new Pinecone index: {index_name}")

# ✅ Load Existing Pinecone Index
vector_db = PineconeVectorStore(index_name=index_name, embedding=OpenAIEmbeddings())  # ✅ Fixed Warning

# ✅ Load spaCy model
nlp = spacy.load("en_core_web_sm")

# ✅ Initialize FastAPI
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Market Research Assistant API is Running"}

@app.get("/bm25_search")
def bm25_endpoint(query: str):
    """Retrieve and rank documents using BM25"""
    return {"bm25_results": rank_documents(query)}

@app.get("/analyze")
def analyze_text(text: str):
    """Analyzes text with spaCy"""
    doc = nlp(text)
    tokens = [{"text": token.text, "pos": token.pos_, "dep": token.dep_} for token in doc]
    return {"tokens": tokens}

@app.get("/vector_search")
def vector_search(query: str, top_k: int = 5):
    """Retrieve top_k relevant documents using Pinecone"""
    docs = vector_db.similarity_search(query, k=top_k)
    return {"vector_results": [doc.page_content for doc in docs]}

@app.get("/hybrid_search")
def hybrid_search(query: str, top_k: int = 5):
    """Combine BM25 and Vector Search results"""
    bm25_results = rank_documents(query)
    vector_results = vector_search(query, top_k)["vector_results"]

    # Combine results by giving weightage (adjust as needed)
    combined_results = list(set(bm25_results + vector_results))

    return {"hybrid_results": combined_results}


@app.get("/rag_generate")
def rag_generate(query: str, top_k: int = 5):
    """RAG Pipeline: Compliance Filtering → Hybrid Retrieval → Live Data → AI Insights"""

    # ✅ Step 1: Apply Compliance Filtering
    filtered_query = compliance_filter(query)  

    # ✅ Step 2: Retrieve Relevant Documents (BM25 + Vector Search)
    retrieved_docs = hybrid_search(filtered_query, top_k)["hybrid_results"]

    # ✅ Step 3: Fetch Live Market News
    live_news = get_live_news(filtered_query)

    # ✅ Step 4: Fetch Google Trends Data
    google_trends_data = get_google_trends()

    # ✅ Step 5: Fetch Yahoo Finance Data
    stock_data = get_stock_data(filtered_query)

    # ✅ Step 6: Format Data Properly
    google_trends_text = "\n".join(google_trends_data) if google_trends_data else "No Google Trends data available."
    stock_data_text = "\n".join([f"{k}: {v}" for k, v in stock_data.items()]) if stock_data else "No Stock Data available."

    # ✅ Step 7: Merge All Context Sources
    combined_context = (
        "\n".join(retrieved_docs + live_news) +
        "\n\n📈 Google Trends:\n" + google_trends_text +
        "\n\n📊 Stock Data:\n" + stock_data_text
    )

    # ✅ Step 8: Generate AI Insights using OpenAI
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI market research assistant. Use the provided data to generate deep market insights."},
                {"role": "user", "content": f"Context:\n{combined_context}\n\nAnswer the query: {filtered_query}"}
            ]
        )

        ai_response = response.choices[0].message.content if response.choices else "AI could not generate a response."

    except Exception as e:
        ai_response = f"Error generating response: {str(e)}"

    # ✅ Step 9: Return All Results
    return {
        "query": filtered_query,
        "retrieved_documents": retrieved_docs,
        "live_news": live_news,
        "google_trends": google_trends_data,
        "yahoo_finance_data": stock_data,
        "ai_generated_response": ai_response
    }


# ✅ Debugging: Print available indexes
print(f"✅ Pinecone connected! Available Indexes: {pc.list_indexes().names()}")
