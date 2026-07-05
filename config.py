import os
from pathlib import Path

# Load .env so GROQ_API_KEY is available
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).with_name(".env"))
except ImportError:
    pass

from langchain_groq import ChatGroq

# Single shared chat model instance used across the app
chat_model = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.environ.get("GROQ_API_KEY"),
)
