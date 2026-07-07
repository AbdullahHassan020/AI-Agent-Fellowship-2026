import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env
load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise Exception("OPENROUTER_API_KEY not found in .env")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

def ask_ai(messages, model):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content