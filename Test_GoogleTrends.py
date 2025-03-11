from pytrends.request import TrendReq

def test_google_trends():
    """Fetch interest over time for a given keyword."""
    pytrends = TrendReq(hl="en-US", tz=360)
    kw_list = ["AAPL"]  # Keywords

    try:
        pytrends.build_payload(kw_list, cat=0, timeframe="now 7-d", geo="US", gprop="")
        data = pytrends.interest_over_time()
        print("✅ Google Trends Data:", data.head())
        return data

    except Exception as e:
        print(f"❌ Error fetching Google Trends: {str(e)}")
        return []

if __name__ == "__main__":
    test_google_trends()
