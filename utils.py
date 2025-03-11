import yfinance as yf
import spacy
from typing import Optional
import re
from fuzzywuzzy import process  # ✅ For fuzzy matching

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# ✅ Define a mapping for well-known companies
COMPANY_TICKER_MAP = {
    "nvidia": ("NVDA", "US"),
    "tesla": ("TSLA", "US"),
    "apple": ("AAPL", "US"),
    "microsoft": ("MSFT", "US"),
    "amazon": ("AMZN", "US"),
    "google": ("GOOGL", "US"),
    "alphabet": ("GOOGL", "US"),
    "tata consultancy services": ("TCS.NS", "IN"),
    "reliance industries": ("RELIANCE.NS", "IN"),
    "infosys": ("INFY.NS", "IN"),
    "hdfc bank": ("HDFCBANK.NS", "IN"),
    "toyota": ("TM", "JP"),
    "samsung": ("005930.KQ", "KR"),
    "vodafone": ("VOD.L", "UK"),
}

# ✅ Global company names for fuzzy matching (expandable)
GLOBAL_COMPANIES = list(COMPANY_TICKER_MAP.keys()) + [
    "Meta", "Netflix", "Berkshire Hathaway", "IBM", "Sony", "Tesla Inc.", "Intel", "Oracle",
    "Bank of America", "JPMorgan Chase", "Goldman Sachs", "PayPal", "Uber", "Zoom Video"
]

def extract_company_name(query: str) -> Optional[str]:
    """
    Extracts a company name from a user query using NLP and fuzzy matching.

    Args:
        query (str): The search query (e.g., "Tell me about NVIDIA stock").

    Returns:
        str: The extracted company name or None if not found.
    """
    query = query.lower()  # ✅ Normalize query to lowercase
    doc = nlp(query)
    company_name = None

    # ✅ Step 1: Try Named Entity Recognition (NER)
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT"]:
            company_name = ent.text.lower()
            print(f"🔍 Detected company name (NER): {company_name}")  # ✅ Debugging log
            break

    # ✅ Step 2: If no direct match, use fuzzy matching
    if not company_name:
        best_match, score = process.extractOne(query, GLOBAL_COMPANIES)
        if score > 75:  # ✅ Use fuzzy matching only if score is high
            print(f"🔍 Fuzzy matched: {best_match} (Score: {score})")  # ✅ Debugging log
            return best_match.lower()

    if not company_name:
        print("⚠️ No company name detected")  # ✅ Debugging log
    return company_name


def lookup_ticker(company_name: str) -> Optional[tuple[str, str]]:
    """
    Finds the stock ticker and country for a given company name.

    Args:
        company_name (str): The company name extracted from the query.

    Returns:
        tuple: (ticker, country) if found, else (None, None).
    """
    # ✅ Step 1: Check predefined mappings
    if company_name in COMPANY_TICKER_MAP:
        return COMPANY_TICKER_MAP[company_name]

    # ✅ Step 2: Use yfinance to find the ticker
    try:
        stock = yf.Ticker(company_name.upper())  # Try uppercase match
        info = stock.info
        if "symbol" in info and info["symbol"]:
            country = info.get("exchangeCountry", "US")  # Default to US if unknown
            return info["symbol"], country
    except Exception:
        pass

    return None, None

def infer_ticker_and_country(query: str) -> tuple[Optional[str], Optional[str]]:
    """
    Infers the stock ticker and country from a user query.

    Args:
        query (str): The user query.

    Returns:
        (ticker, country) tuple.
    """
    print(f"🔎 Inferring ticker from query: {query}")  # ✅ Debugging log
    company_name = extract_company_name(query)
    if not company_name:
        print("⚠️ No company found in query")  # ✅ Debugging log
        return None, None

    ticker, country = lookup_ticker(company_name)
    print(f"✅ Inferred: {company_name} → {ticker}, {country}")  # ✅ Debugging log
    return ticker, country




def get_company_name_from_ticker(ticker: str) -> Optional[str]:
    """
    Retrieve the company name from a given stock ticker symbol using Yahoo Finance.

    Args:
        ticker (str): Stock ticker symbol (e.g., "AAPL").

    Returns:
        Optional[str]: Company name (e.g., "Apple Inc.") or None if not found.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get("longName", None)  # Return the full company name
    except Exception as e:
        print(f"❌ Error fetching company name for {ticker}: {e}")
        return None

# ✅ Testing Fixes
if __name__ == "__main__":
    print("✅ Testing Ticker Inference with Fallbacks")
    print(infer_ticker_and_country("Tell me about NVIDIA"))   # Expected: ("NVDA", "US")
    print(infer_ticker_and_country("Market details for Tesla"))  # Expected: ("TSLA", "US")
    print(infer_ticker_and_country("Stock price of Infosys"))  # Expected: ("INFY.NS", "IN")
    print(infer_ticker_and_country("How is Toyota performing?"))  # Expected: ("TM", "JP")
    print(infer_ticker_and_country("What is the latest news on Meta?"))  # Expected: ("META", "US")
    print(infer_ticker_and_country("Give me details on an unknown company"))  # Expected: (None, None)
