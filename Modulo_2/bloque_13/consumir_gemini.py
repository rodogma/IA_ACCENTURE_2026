
import os
import re
import json
import requests

from dotenv import load_dotenv

load_dotenv(override=True)


def calcular_costo_peticion(
    datos: dict,
    precio_entrada: float,
    precio_salida: float
) -> float:

    uso = datos.get("usageMetadata")

    if not isinstance(uso, dict):
        raise ValueError(
            "Gemini no devolvió usageMetadata."
        )

    tokens_entrada = uso.get("promptTokenCount", 0)
    tokens_salida = uso.get("candidatesTokenCount", 0)

    costo_entrada = tokens_entrada * precio_entrada
    costo_salida = tokens_salida * precio_salida

    costo_total = costo_entrada + costo_salida

    print(f"Tokens entrada: {tokens_entrada}")
    print(f"Tokens salida: {tokens_salida}")
    print(f"Costo entrada: ${costo_entrada:.6f}")
    print(f"Costo salida: ${costo_salida:.6f}")

    return costo_total


def armar_peticion(
    pregunta: str,
    system_instruction: str = "",
    response_schema: dict = None
) -> tuple[str, dict]:

    if not isinstance(pregunta, str):
        raise ValueError(
            "La pregunta debe ser una cadena de texto."
        )

    if not pregunta.strip():
        raise ValueError(
            "La pregunta no puede estar vacía."
        )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "No se encontró GEMINI_API_KEY en .env."
        )

    modelo = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.5-flash-lite"
    ).strip()

    print(f"Modelo utilizado: {modelo}")

    url = (
        "https://generativelanguage.googleapis.com"
        f"/v1beta/models/{modelo}:generateContent"
    )

    body = {
        "contents": [
            {
                "parts": [
                    {"text": pregunta}
                ]
            }
        ]
    }

    if system_instruction:
        body["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }

    return url, body


def enviar_peticion(url: str, body: dict) -> dict:

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Falta GEMINI_API_KEY.")

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    try:
        respuesta = requests.post(
            url,
            json=body,
            headers=headers,
            timeout=10
        )

    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError
    ) as error:
        raise TimeoutError(
            f"Error de conexión: {error}"
        ) from error

    codigo = respuesta.status_code

    try:
        datos = respuesta.json()
    except ValueError:
        datos = {}

    if not respuesta.ok:

        detalle = (
            datos.get("error", {})
            if isinstance(datos, dict)
            else {}
        )

        mensaje = (
            detalle.get("message", respuesta.reason)
            if isinstance(detalle, dict)
            else respuesta.reason
        )

        if codigo in (401, 403):
            raise ValueError(
                f"Error de autenticación HTTP {codigo}: {mensaje}"
            )

        if codigo == 429:
            raise TimeoutError(
                f"Límite de peticiones HTTP 429: {mensaje}"
            )

        if codigo == 408 or codigo >= 500:
            raise TimeoutError(
                f"Error temporal HTTP {codigo}: {mensaje}"
            )

        raise RuntimeError(
            f"Error HTTP {codigo}: {mensaje}"
        )

    if not isinstance(datos, dict):
        raise RuntimeError(
            "La respuesta de Gemini no es un objeto JSON."
        )

    if "error" in datos:
        raise RuntimeError(
            f"Error de Gemini: {datos['error']}"
        )

    return datos


def extraer_texto(datos: dict) -> str:

    uso = datos.get("usageMetadata", {})

    if isinstance(uso, dict):
        print(
            "Tokens prompt:",
            uso.get("promptTokenCount", 0)
        )
        print(
            "Tokens candidates:",
            uso.get("candidatesTokenCount", 0)
        )
        print(
            "Tokens total:",
            uso.get("totalTokenCount", 0)
        )
    else:
        print("Aviso: no se recibió usageMetadata.")

    candidatos = datos.get("candidates", [])

    if not candidatos:
        raise RuntimeError(
            "Gemini no devolvió candidatos."
        )

    partes = (
        candidatos[0]
        .get("content", {})
        .get("parts", [])
    )

    textos = [
        parte["text"]
        for parte in partes
        if isinstance(parte, dict)
        and isinstance(parte.get("text"), str)
    ]

    if not textos:
        raise RuntimeError(
            "Gemini no devolvió contenido de texto."
        )

    return "\n".join(textos)


def parsear_respuesta_json(texto: str) -> dict:

    texto_limpio = texto.strip()

    texto_limpio = re.sub(
        r"^```(?:json)?\s*",
        "",
        texto_limpio
    )

    texto_limpio = re.sub(
        r"\s*```$",
        "",
        texto_limpio
    )

    try:
        datos = json.loads(texto_limpio)

    except json.JSONDecodeError as error:
        raise ValueError(
            "La respuesta no es JSON válido."
        ) from error

    if not isinstance(datos, dict):
        raise ValueError(
            "La respuesta JSON debe ser un objeto."
        )

    if "rta" not in datos or "fuente" not in datos:
        raise ValueError(
            "La respuesta no contiene rta y fuente."
        )

    return datos


if __name__ == "__main__":
    print("Módulo consumir_gemini cargado correctamente.")
