# streamlit_app.py
import streamlit as st
import requests

# FastAPI Backend URL
FASTAPI_URL = "http://127.0.0.1:8000"

st.title("🔍 Market Research Assistant")
st.write("Enter a search query, and get AI-powered insights. Optionally specify a ticker or country.")

# Text area for free-form query
query_input = st.text_area("Enter your query:", "How is AI impacting cloud computing?")

# Manual Stock Ticker Input
ticker_selected = st.text_input("Enter a stock ticker (optional):", placeholder="e.g., TSLA, TCS.NS")

# Optional Country Dropdown
country_options = ["", "US", "IN", "JP", "CH", "UK"]  # Empty option means not selected
country_selected = st.selectbox("Select a country (optional):", country_options, index=0, help="e.g., US, India (IN), Japan (JP)")

if st.button("Get Insights"):
    if query_input.strip():
        with st.spinner("🔄 Fetching AI-powered insights... Please wait."):  # ✅ Loading Indicator
            # Build query parameters
            params = {"query": query_input.strip()}
            if ticker_selected.strip():  # Only add ticker if user provides one
                params["ticker"] = ticker_selected.strip().upper()
            if country_selected:  # Only add country if selected
                params["country"] = country_selected

            # Send request to FastAPI
            response = requests.get(f"{FASTAPI_URL}/rag_generate", params=params)

        if response.status_code == 200:
            result = response.json()

            # ✅ Improved AI response display
            ai_response = result.get("ai_generated_response", "No response generated.")
            st.success("✅ AI-Powered Insights:")
            st.markdown(f"🧠 **Response:**\n\n{ai_response}")  # ✅ Markdown for better readability

            # ✅ Display Financial Data in a Table (Better Readability)
            yahoo_finance_data = result.get("yahoo_finance_data", {})
            if yahoo_finance_data:
                st.write("### 📊 Yahoo Finance Data")
                st.table(yahoo_finance_data)  # ✅ Display neatly in a table

            # ✅ Improved Debugging Information
            st.write("### 📢 Additional Insights")
            st.json({
                "Original Query": result.get("original_query", "N/A"),
                "Filtered Query": result.get("filtered_query", "N/A"),
                "Effective Ticker": result.get("effective_ticker", "N/A"),
                "Google Trends": result.get("google_trends", []),
                "Live News Articles": result.get("live_news", [])
            })

        else:
            # ✅ Improved error handling with a user-friendly message
            st.error("🚨 Unable to fetch insights. The server might be busy. Please try again later.")
    else:
        st.error("⚠️ Please enter a query.")

st.markdown("---")
st.caption("🚀 Powered by FastAPI & Streamlit")
