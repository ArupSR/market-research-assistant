from dotenv import load_dotenv
import os

# ✅ Load environment variables
load_dotenv()

# ✅ Check if the key is loadedfrom dotenv import load_dotenv
import os

# ✅ Load environment variables
load_dotenv()

# ✅ Print environment variables
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
print("PINECONE_API_KEY:", os.getenv("PINECONE_API_KEY"))
print("NEWS_API_KEY:", os.getenv("NEWS_API_KEY"))

news_api_key = os.getenv("NEWS_API_KEY")

if not news_api_key:
    print("❌ ERROR: NEWS_API_KEY is missing. Make sure it's set in the .env file.")
else:
    print(f"✅ NEWS_API_KEY Loaded Successfully: {news_api_key[:5]}******")  # Mask for security
