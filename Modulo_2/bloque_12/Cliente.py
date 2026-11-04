
import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("No se encontró GEMINI_API_KEY en el archivo .env")

# Modelo Gemini
URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.8-flash:generateContent"
)

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": GEMINI_API_KEY
}


def enviar_peticion(cuerpo):
    try:
        respuesta = requests.post(
            URL,
            json=cuerpo,
            headers=headers,
            timeout=(10, 60)
        )

    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError
    ) as e:
        raise TimeoutError(
            f"No se pudo conectar con Gemini: {e}"
        ) from e

    print("Código HTTP:", respuesta.status_code)

    if respuesta.status_code in (401, 403):
        raise ValueError(
            "Credencial inválida o sin permisos. Revisa tu API KEY."
        )

    if respuesta.status_code == 429:
        raise TimeoutError(
            f"HTTP 429 - Límite de uso o cuota: {respuesta.text[:500]}"
        )

    if respuesta.status_code >= 500:
        raise TimeoutError(
            f"HTTP {respuesta.status_code} - Error del servidor."
        )

    respuesta.raise_for_status()

    return respuesta.json()


if __name__ == "__main__":

    cuerpo = {
        "contents": [
            {
                "parts": [
                    {"text": "Hola"}
                ]
            }
        ]
    }

    try:
        resultado = enviar_peticion(cuerpo)
        print("Respuesta de Gemini:")
        print(resultado)

    except (TimeoutError, ValueError, requests.exceptions.HTTPError) as e:
        print("Error:", e)
