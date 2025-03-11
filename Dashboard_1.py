import streamlit as st
import requests

# FastAPI Backend URL
FASTAPI_URL = "http://127.0.0.1:8000"

st.title("📊 Market Research Assistant")
st.write("Analyze text and generate market insights using AI.")

# 🔹 Text Input for Analysis
st.subheader("🔍 Text Analysis with spaCy")
text_input = st.text_area("Enter text for analysis:", "Apple is launching a new AI-powered MacBook.")

if st.button("Analyze"):
    if text_input.strip():
        response = requests.get(f"{FASTAPI_URL}/analyze", params={"text": text_input})
        if response.status_code == 200:
            tokens = response.json()["tokens"]
            st.json(tokens)
        else:
            st.error("Error analyzing text. Check backend.")

# 🔹 Query Input for OpenAI Insights
st.subheader("💡 Generate Market Insights with OpenAI")
query_input = st.text_area("Enter a market research query:", "What are the latest trends in AI-powered devices?")

if st.button("Generate Insights"):
    if query_input.strip():
        response = requests.get(f"{FASTAPI_URL}/generate", params={"query": query_input})
        if response.status_code == 200:
            st.success("✅ AI Insights Generated:")
            st.write(response.json()["insight"])
        else:
            st.error("Error generating insights. Check backend.")

# 🔹 BM25 Search
st.subheader("📖 BM25 Keyword-Based Search")
bm25_query = st.text_input("Enter your search query for BM25:", "AI in finance")

if st.button("Search with BM25"):
    if bm25_query.strip():
        response = requests.get(f"{FASTAPI_URL}/bm25_search", params={"query": bm25_query})
        if response.status_code == 200:
            st.success("✅ BM25 Search Results:")
            st.write(response.json()["bm25_results"])
        else:
            st.error("Error with BM25 search. Check backend.")

# 🔹 Vector Search
st.subheader("🔬 Vector Search with Pinecone")
vector_query = st.text_input("Enter your query for vector search:", "Cloud computing trends")

if st.button("Search with Vector"):
    if vector_query.strip():
        response = requests.get(f"{FASTAPI_URL}/vector_search", params={"query": vector_query})
        if response.status_code == 200:
            st.success("✅ Vector Search Results:")
            st.write(response.json()["vector_results"])
        else:
            st.error("Error with vector search. Check backend.")

# 🔹 Hybrid Search
st.subheader("⚡ Hybrid Search (BM25 + Vector Search)")
hybrid_query = st.text_input("Enter your query for hybrid search:", "Market research in AI")

if st.button("Search with Hybrid"):
    if hybrid_query.strip():
        response = requests.get(f"{FASTAPI_URL}/hybrid_search", params={"query": hybrid_query})
        if response.status_code == 200:
            st.success("✅ Hybrid Search Results:")
            st.write(response.json()["hybrid_results"])
        else:
            st.error("Error with hybrid search. Check backend.")

# 🔹 RAG-Based AI Response
st.subheader("🧠 RAG-Based AI Market Insights")
rag_query = st.text_input("Enter your question for RAG retrieval:", "How is AI impacting cloud computing?")

if st.button("Generate AI Insights with RAG"):
    if rag_query.strip():
        response = requests.get(f"{FASTAPI_URL}/rag_generate", params={"query": rag_query})
        if response.status_code == 200:
            result = response.json()
            st.success("✅ RAG-Based AI Insights:")
            st.write("🔹 **Relevant Documents Retrieved:**")
            st.write(result["retrieved_docs"])
            st.write("📝 **AI-Generated Response:**")
            st.write(result["answer"])
        else:
            st.error("Error with RAG-based insights. Check backend.")

st.markdown("---")
st.caption("🚀 Powered by FastAPI & Streamlit")
