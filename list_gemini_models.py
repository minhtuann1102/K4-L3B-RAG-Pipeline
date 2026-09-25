"""List available Gemini models."""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Fetching available models...")
models = client.models.list()

print("\nAvailable embedding models:")
for model in models:
    if "embedding" in model.name.lower():
        print(f"  - {model.name}")
        print(f"    Display name: {model.display_name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"    Methods: {model.supported_generation_methods}")
        print()
