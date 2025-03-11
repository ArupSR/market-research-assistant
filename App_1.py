from fastapi import FastAPI
import spacy
import openai
import os
import pinecone
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore as PineconeStore  # Updated import
from langchain_openai import OpenAIEmbeddings

# Load environment variables
load_dotenv()

# Load Pinecone API Key
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("❌ ERROR: Pinecone API Key is missing. Add it to .env file.")

# Load OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: OpenAI API Key is missing. Add it to .env file.")

# Initialize Pinecone
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)

# Define Index
index_name = "market-research"

# Check if Index Exists, Else Create It
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
    )
    print(f"✅ Created new Pinecone index: {index_name}")

# Load Existing Pinecone Index
pinecone_index = pc.Index(index_name)
# Updated PineconeStore initialization with text_key
vector_db = PineconeStore(pinecone_index, embedding=OpenAIEmbeddings(), text_key="text")

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Initialize FastAPI
App_1 = FastAPI()

@App_1.get("/")
def home():
    return {"message": "Market Research Assistant API is Running"}

@App_1.get("/analyze")
def analyze_text(text: str):
    """Analyzes text with spaCy"""
    doc = nlp(text)
    tokens = [{"text": token.text, "pos": token.pos_, "dep": token.dep_} for token in doc]
    return {"tokens": tokens}

@App_1.get("/generate")
def generate_insights(query: str):
    """Uses OpenAI's API to generate insights"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": query}]
    )
    return {"insight": response.choices[0].message.content}

@App_1.get("/search")
def search_documents(query: str, top_k: int = 5):
    """Retrieve top_k relevant documents using Pinecone"""
    docs = vector_db.similarity_search(query, k=top_k)
    return {"results": [doc.page_content for doc in docs]}

# Debugging: Print available indexes
print(f"✅ Pinecone connected! Available Indexes: {pc.list_indexes().names()}")