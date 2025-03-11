from utils import infer_ticker_and_country, get_company_name_from_ticker  # ✅ Import necessary functions
import yfinance as yf

def get_stock_data(query: str, country: str = "US"):
    """
    Fetch stock data for the inferred ticker.
    
    Args:
        query (str): The user query (e.g., "Provide market details for TCS").
        country (str): The country code to determine exchange (default: US).
    
    Returns:
        dict: Stock data including price, market cap, etc.
    """
    ticker, inferred_country = infer_ticker_and_country(query)  # ✅ Extract only ticker
    country = country or inferred_country  # ✅ Use inferred country if not provided

    if not ticker:
        return {"error": "Unable to determine stock ticker from query"}

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "symbol": info.get("symbol", ticker),
            "name": get_company_name_from_ticker(ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "price": info.get("currentPrice", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
        }
    except Exception as e:
        print(f"❌ Yahoo Finance error for {ticker}: {e}")
        return {"error": f"Failed to fetch data for {ticker}: {str(e)}"}

# Example Test Cases
if __name__ == "__main__":
    print("✅ Testing Stock Data Retrieval")
    print(get_stock_data("Provide market details for TCS", "IN"))  # Expected: Stock data for TCS.NS
    print(get_stock_data("Tesla stock price"))                    # Expected: Stock data for TSLA
    print(get_stock_data("Random text"))                          # Expected: {"error": "Unable to determine stock ticker from query"}
