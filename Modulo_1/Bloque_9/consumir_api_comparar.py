
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Ruta al archivo .env principal del proyecto
ruta_env = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ruta_env)


def armar_peticion(pregunta, modelo="gemini-3.5-flash-lite"):
    if not isinstance(pregunta, str):
        raise TypeError("La pregunta debe ser una cadena de texto.")

    if not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("No se encontró GEMINI_API_KEY en .env")

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{modelo}:generateContent"
    )

    body = {
        "contents": [
            {"parts": [{"text": pregunta}]}
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    return url, body, headers


def enviar_peticion(url, body, headers):
    respuesta = requests.post(
        url,
        json=body,
        headers=headers,
        timeout=60
    )

    respuesta.raise_for_status()
    return respuesta.json()


def extraer_texto(datos):
    try:
        partes = datos["candidates"][0]["content"]["parts"]

        texto = "\n".join(
            parte["text"]
            for parte in partes
            if "text" in parte
        )

        if not texto:
            raise ValueError("Gemini no devolvió texto.")

        return texto

    except (KeyError, IndexError, TypeError) as error:
        raise ValueError(
            "La respuesta de Gemini no tiene el formato esperado."
        ) from error


def calcular_costo(datos, precio_entrada, precio_salida):
    uso = datos.get("usageMetadata")

    if not uso:
        raise ValueError("No se recibió usageMetadata.")

    entrada = uso.get("promptTokenCount", 0)
    total = uso.get("totalTokenCount")

    if total is not None:
        salida = max(0, total - entrada)
    else:
        salida = (
            uso.get("candidatesTokenCount", 0)
            + uso.get("thoughtsTokenCount", 0)
        )

    costo = (
        entrada * precio_entrada
        + salida * precio_salida
    )

    return costo


def obtener_dato_de_prueba(
    pregunta,
    modelo="gemini-3.5-flash-lite"
):
    url, body, headers = armar_peticion(pregunta, modelo)
    datos = enviar_peticion(url, body, headers)

    return extraer_texto(datos)
