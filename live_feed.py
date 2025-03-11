import requests
import os

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"

def get_live_news(query: str) -> list:
    """
    Fetches live news articles related to the query, ensuring high relevance.

    Args:
        query (str): Search term for news.

    Returns:
        list: Top 5 most relevant NVIDIA-related news headlines.
    """
    if not NEWS_API_KEY:
        return ["⚠️ Error: Missing News API Key"]

    params = {
        "q": query,
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": 20,  # ✅ Fetch 20 to filter properly
        "apiKey": NEWS_API_KEY
    }

    try:
        response = requests.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if "articles" in data:
            # ✅ Strict filtering for NVIDIA mentions in both title & description
            filtered_articles = [
                article["title"]
                for article in data["articles"]
                if "nvidia" in article["title"].lower() or "nvidia" in article["description"].lower()
            ]

            if len(filtered_articles) < 5:
                return filtered_articles + ["⚠️ Not enough NVIDIA-specific news."]

            return filtered_articles[:5]  # ✅ Only top 5 NVIDIA-related news

        return ["⚠️ No relevant news found."]

    except requests.exceptions.RequestException as e:
        return [f"Error fetching news: {str(e)}"]


# ✅ Test Fix
if __name__ == "__main__":
    print(get_live_news("NVIDIA"))  # Expected: 5 relevant NVIDIA news articles
