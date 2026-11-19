
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: No se encontró GEMINI_API_KEY.")
    raise SystemExit(1)

url = "https://generativelanguage.googleapis.com/v1beta/models"

try:
    respuesta = requests.get(
        url,
        headers={"x-goog-api-key": api_key},
        timeout=20
    )

    print("Código HTTP:", respuesta.status_code)

    if not respuesta.ok:
        error = respuesta.json()
        print("ERROR:", error.get("error", {}).get("message"))
        raise SystemExit(1)

    datos = respuesta.json()

    print("\nMODELOS DISPONIBLES:")

    for modelo in datos.get("models", []):
        if "generateContent" in modelo.get(
            "supportedGenerationMethods", []
        ):
            print(modelo["name"])

except requests.exceptions.RequestException as error:
    print("ERROR DE CONEXIÓN:", error)
