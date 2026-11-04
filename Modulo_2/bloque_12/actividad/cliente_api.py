
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def armar_peticion(
    pregunta: str,
    system_instruction: str = ""
) -> tuple[str, dict]:

    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta debe ser un texto válido.")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "No se encontró GEMINI_API_KEY en el archivo .env"
        )

    modelo = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{modelo}:generateContent"
    )

    cuerpo = {
        "contents": [
            {"parts": [{"text": pregunta}]}
        ]
    }

    if system_instruction:
        cuerpo["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    return url, cuerpo


def enviar_peticion(url: str, cuerpo: dict) -> dict:

    api_key = os.getenv("GEMINI_API_KEY")

    try:
        respuesta = requests.post(
            url,
            json=cuerpo,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key
            },
            timeout=(10, 60)
        )

    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError
    ) as error:
        raise TimeoutError(
            "Error de conexión o tiempo de espera."
        ) from error

    print("Código HTTP:", respuesta.status_code)

    if respuesta.status_code in (401, 403):
        raise ValueError(
            "Credencial inválida o sin permiso. "
            "Revisa tu GEMINI_API_KEY."
        )

    if respuesta.status_code == 429:
        raise TimeoutError(
            "Se alcanzó el límite de uso de Gemini."
        )

    if respuesta.status_code >= 500:
        raise TimeoutError(
            "Error temporal del servidor Gemini."
        )

    respuesta.raise_for_status()

    return respuesta.json()


def extraer_texto(datos: dict) -> str:

    try:
        partes = datos["candidates"][0]["content"]["parts"]

        textos = [
            parte["text"]
            for parte in partes
            if "text" in parte
        ]

        if not textos:
            raise ValueError(
                "Gemini no devolvió una respuesta de texto."
            )

        return "\n".join(textos)

    except (KeyError, IndexError, TypeError) as error:
        raise ValueError(
            "No se pudo extraer el texto."
        ) from error
