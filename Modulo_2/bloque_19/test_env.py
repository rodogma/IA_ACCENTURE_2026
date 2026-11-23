import os
from dotenv import load_dotenv

load_dotenv()

print("API KEY cargada:", bool(os.getenv("GEMINI_API_KEY")))
print("Modelo:", os.getenv("GEMINI_MODEL"))