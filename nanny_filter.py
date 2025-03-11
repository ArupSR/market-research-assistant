# nanny_filter.py
import re
import logging
from typing import Optional
from utils import get_company_name_from_ticker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compliance_filter(query: str, ticker: Optional[str] = None) -> str:
    """Filters queries for compliance and prioritizes ticker if provided."""
    query = query.strip()
    if not query:
        logger.warning("Empty query received")
        return "Query blocked: Empty input"

    # Define banned terms
    banned_terms = [
        "kill", "murder", "death", "assassinate", "bomb", "terror", "illegal",
        "fraud", "scam", "manipulate", "insider", "launder",
        "hate", "racist", "discriminate", "offensive", "nsfw",
        "sex", "porn", "gambling"
    ]
    query_lower = query.lower()
    for term in banned_terms:
        if term in query_lower:
            logger.warning(f"Query blocked due to non-compliant term: '{term}' in '{query}'")
            return f"Query blocked: Contains non-compliant term '{term}'"

    # Ticker pattern
    ticker_pattern = r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$'

    # Prioritize UI-provided ticker if present
    if ticker and re.match(ticker_pattern, ticker):
        company_name = get_company_name_from_ticker(ticker)
        logger.info(f"Using UI-provided ticker '{ticker}' (Company: '{company_name}')")
        return ticker

    # Extract ticker from query if present
    words = query.split()
    for word in words:
        if re.match(ticker_pattern, word):
            company_name = get_company_name_from_ticker(word)
            logger.info(f"Extracted ticker '{word}' (Company: '{company_name}') from '{query}'")
            return word

    # No ticker found, return full query for general processing
    logger.info(f"No ticker detected in '{query}', passing as-is")
    return query

if __name__ == "__main__":
    tests = [
        ("TSLA", None), ("Provide market details of TCS", None),
        ("How is AI used by Tesla", "TSLA"), ("kill TCS", None),
        ("Random text", None), ("TCS.NS details", "TCS.NS")
    ]
    for q, t in tests:
        print(f"Query: '{q}', Ticker: '{t}' → Result: '{compliance_filter(q, t)}'")