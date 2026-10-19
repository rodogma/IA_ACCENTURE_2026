from dotenv import load_dotenv # importaciones del modulo dotenv
import os

from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    print("✅ API Key cargada correctamente")
else:
    print("❌ No se encontró la API Key")
