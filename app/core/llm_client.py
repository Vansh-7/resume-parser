import os
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

# initialize the ASYNC client exactly once here
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"