import openai

openai.api_key = "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"  # Replace with your actual key

try:
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Try "gpt-4" or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print("✅ Model is working!")
except openai.error.OpenAIError as e:
    print(f"❌ Error: {e}")