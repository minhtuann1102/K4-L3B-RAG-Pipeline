"""Test Gemini embedding API."""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("X GEMINI_API_KEY not found in .env")
    exit(1)

print(f"OK API Key found: {api_key[:10]}...")

client = genai.Client(api_key=api_key)

# Test with simple texts
test_texts = ["What are the apartment owner rights?", "What is the apartment regulation?"]

print(f"\nTest with {len(test_texts)} texts")
print("Calling Gemini API...")

try:
    response = client.models.embed_content(
        model="models/gemini-embedding-2",
        contents=test_texts
    )
    
    print(f"OK Number of embeddings: {len(response.embeddings)}")
    
    for i, emb in enumerate(response.embeddings):
        print(f"OK Embedding {i+1} dimension: {len(emb.values)}")
        print(f"   First 5 values: {emb.values[:5]}")
    
    print(f"\nOK Gemini embedding works!")
    
except Exception as e:
    print(f"X Error: {e}")
    import traceback
    traceback.print_exc()
