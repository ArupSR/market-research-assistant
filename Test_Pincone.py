import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

# Get API Key
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("❌ ERROR: Pinecone API Key is missing. Add it to .env file.")

# Initialize Pinecone Client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Define index name
index_name = "market-research"

# ✅ Use AWS free-tier supported region (us-east-1)
region = "us-east-1"

# Check if index exists, else create it
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # Adjust based on embedding model
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=region)
    )
    print(f"✅ Index '{index_name}' created in AWS {region}")

# Get index reference
index = pc.Index(index_name)

# Print available indexes
print(f"✅ Pinecone connected! Available Indexes: {pc.list_indexes().names()}")
