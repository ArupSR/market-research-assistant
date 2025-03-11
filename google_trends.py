from pytrends.request import TrendReq
import time
import json
import os

# ✅ Setup cache file to prevent excessive API requests
CACHE_FILE = "google_trends_cache.json"

def load_cache():
    """Loads cached Google Trends data. Creates file if it does not exist."""
    if not os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "w") as f:
            json.dump({}, f)  # ✅ Initialize empty cache
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

def save_cache(cache):
    """Saves Google Trends data to cache safely."""
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)  # ✅ Ensure data is formatted properly
        f.flush()  # ✅ Force immediate write to file
    print(f"✅ Cache updated successfully.")

def get_google_trends(query: str) -> list:
    """
    Fetch Google Trends data with caching to avoid hitting API rate limits.

    Args:
        query (str): The search query.

    Returns:
        list: A list of Google Trends data points.
    """
    pytrends = TrendReq(hl="en-US", tz=360)
    cache = load_cache()

    # ✅ Check cache first before making a new request
    if query in cache and cache[query]:
        print(f"✅ Using cached Google Trends data for '{query}'")
        return cache[query]

    retries = 3  # ✅ Reduce retries to avoid excessive waiting
    for attempt in range(retries):
        try:
            print(f"🔍 Fetching Google Trends data for '{query}' (Attempt {attempt + 1})")
            pytrends.build_payload(kw_list=[query], timeframe="today 1-m", geo="US")
            interest_data = pytrends.interest_over_time()

            if not interest_data.empty:
                trends = [f"{query}: {int(val)}" for val in interest_data[query].tail(5)]
                
                # ✅ Save to cache immediately
                cache[query] = trends
                save_cache(cache)

                return trends if trends else [f"⚠️ No significant trends for '{query}'"]

            return [f"⚠️ No Google Trends data available for '{query}'"]

        except Exception as e:
            if "429" in str(e):  # ✅ Handle rate limit
                wait_time = 60  # ✅ Increase wait time
                print(f"⚠️ Google Trends rate limit hit. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return [f"Error fetching Google Trends for '{query}': {str(e)}"]

    return ["⚠️ Google Trends API rate limit exceeded. Please try again later."]

# ✅ Test Fix
if __name__ == "__main__":
    print(get_google_trends("NVIDIA"))  # Expected: Cached trends or live results
