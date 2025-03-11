# app.py
from fastapi import FastAPI
from typing import Optional
import spacy
import openai
import os
import pinecone
import re
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from bm25_search import rank_documents
from nanny_filter import compliance_filter
from live_feed import get_live_news
from google_trends import get_google_trends
from yahoo_finance import get_stock_data
from hybrid_search import hybrid_search
from utils import infer_ticker_and_country
from utils import get_company_name_from_ticker
from google_trends import load_cache


# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not PINECONE_API_KEY or not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: Missing API keys in .env file.")

# Initialize Pinecone
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
index_name = "market-research"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
    )
vector_db = PineconeVectorStore(index_name=index_name, embedding=OpenAIEmbeddings())

# Load spaCy
nlp = spacy.load("en_core_web_sm")

# Initialize FastAPI
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Market Research Assistant API is Running"}

@app.get("/bm25_search")
def bm25_endpoint(query: str):
    return {"bm25_results": rank_documents(query)}

@app.get("/analyze")
def analyze_text(text: str):
    doc = nlp(text)
    tokens = [{"text": token.text, "pos": token.pos_, "dep": token.dep_} for token in doc]
    return {"tokens": tokens}

@app.get("/vector_search")
def vector_search(query: str, top_k: int = 5):
    docs = vector_db.similarity_search(query, k=top_k)
    return {"vector_results": [doc.page_content for doc in docs]}

@app.get("/hybrid_search")
def hybrid_search_endpoint(query: str, top_k: int = 5):
    return hybrid_search(query, top_k)

@app.get("/rag_generate")
def rag_generate(query: str, ticker: Optional[str] = None, country: Optional[str] = None, top_k: int = 5):
    """
    Generates a market research response based on query, automatically inferring missing ticker & country.
    """
    filtered_query = compliance_filter(query, ticker)
    print(f"Filtered query: {filtered_query}")
    
    if "Query blocked" in filtered_query:
        return {"error": filtered_query}

    # ✅ Step 1: Infer ticker & country if not provided
    if not ticker or not country:
        inferred_ticker, inferred_country = infer_ticker_and_country(filtered_query)
        ticker = ticker or inferred_ticker
        country = country or inferred_country

    print(f"Effective ticker: {ticker}, Country: {country}")

    # ✅ Step 2: If no ticker was found, return an error
    if not ticker:
        return {"error": "No valid company ticker could be determined from the query."}

    # ✅ Step 3: Fetch data
    retrieved_docs = hybrid_search(filtered_query, top_k)["hybrid_results"]
    live_news = [news for news in get_live_news(filtered_query) if not news.startswith("⚠️")]

    # ✅ Step 3.1: Use Cached Google Trends Data (Avoid Unnecessary Calls)
    google_trends_cache = load_cache()
    try:
        google_trends_data = google_trends_cache.get(ticker, get_google_trends(ticker or filtered_query))
    except Exception as e:
        google_trends_data = [f"⚠️ Google Trends Error: {str(e)}"]

    stock_data = get_stock_data(ticker) if ticker else {"message": "No valid ticker detected for stock data"}

    # ✅ Step 4: Build context
    combined_context = "\n".join(retrieved_docs + live_news) + "\n\nGoogle Trends:\n" + "\n".join(google_trends_data) + \
                       "\n\nStock Data:\n" + "\n".join([f"{k}: {v}" for k, v in stock_data.items()])
    if country:
        combined_context += f"\n\nCountry Context: {country}"

    # ✅ Step 5: AI-generated response
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Use the provided context to answer queries accurately."},
                      {"role": "user", "content": f"Context:\n{combined_context}\n\nAnswer the query: {query}"}]
        )
        ai_response = response.choices[0].message.content

        # ✅ Improved AI response formatting
        ai_response = " ".join(ai_response.split())  # Removes extra newlines & multiple spaces


    except Exception as e:
        ai_response = f"Error generating response: {str(e)}"

    return {
        "original_query": query,
        "filtered_query": filtered_query,
        "effective_ticker": ticker,
        "inferred_country": country,
        "retrieved_documents": retrieved_docs,
        "live_news": live_news,
        "google_trends": google_trends_data,
        "yahoo_finance_data": stock_data,
        "ai_generated_response": ai_response
    }


print(f"✅ Pinecone connected! Available Indexes: {pc.list_indexes().names()}")
