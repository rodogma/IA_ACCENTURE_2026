
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Falta GEMINI_API_KEY en .env")

url = "https://generativelanguage.googleapis.com/v1beta/models"

try:
    respuesta = requests.get(
        url,
        params={"key": api_key},
        timeout=30
    )

    respuesta.raise_for_status()

    for modelo in respuesta.json().get("models", []):
        metodos = modelo.get(
            "supportedGenerationMethods", []
        )

        if "generateContent" in metodos:
            print(modelo["name"])

except requests.RequestException as error:
    print(f"ERROR: {error}")
