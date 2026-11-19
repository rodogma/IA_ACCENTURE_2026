# cliente.py

import os
import time
import requests

from dotenv import load_dotenv
from cliente_api import armar_peticion, extraer_texto


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

MODELO = (
    os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite").strip()
    or "gemini-3.1-flash-lite"
)

URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODELO}:generateContent"
)

# Costo ilustrativo para la actividad.
# No representa una tarifa oficial de Google.
COSTO_POR_1000_TOKENS = 0.002

costo_total_sesion = 0.0


def enviar_peticion(cuerpo):
    if not GEMINI_API_KEY:
        raise ValueError("Falta GEMINI_API_KEY en .env")

    try:
        respuesta = requests.post(
            URL,
            params={"key": GEMINI_API_KEY},
            json=cuerpo,
            timeout=30
        )

    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError
    ) as error:
        raise TimeoutError(
            "Error de conexión con Gemini"
        ) from error

    if respuesta.status_code in (401, 403):
        raise ValueError(
            "Credencial inválida o sin permisos"
        )

    if respuesta.status_code == 429:
        raise TimeoutError(
            "Límite de uso alcanzado"
        )

    if respuesta.status_code >= 500:
        raise TimeoutError(
            "Error temporal del servidor"
        )

    if respuesta.status_code in (400, 404):
        raise ValueError(
            f"Error HTTP {respuesta.status_code}: "
            f"{respuesta.text}"
        )

    respuesta.raise_for_status()
    return respuesta.json()


def con_reintento(funcion, intentos=3, espera_base=0.2):
    if intentos < 1:
        raise ValueError("intentos debe ser mayor que cero")

    for intento in range(intentos):
        try:
            return funcion()

        except TimeoutError:
            if intento == intentos - 1:
                raise

            time.sleep(
                espera_base * (2 ** intento)
            )


def registrar_costo(respuesta):
    global costo_total_sesion

    tokens = respuesta.get(
        "usageMetadata", {}
    ).get("totalTokenCount", 0)

    costo = (
        tokens / 1000
    ) * COSTO_POR_1000_TOKENS

    costo_total_sesion += costo

    return costo


def consultar_modelo(pregunta, system_instruction=""):
    cuerpo = armar_peticion(
        pregunta,
        system_instruction
    )

    try:
        respuesta = con_reintento(
            lambda: enviar_peticion(cuerpo)
        )

    except TimeoutError as error:
        raise RuntimeError(
            "Gemini no respondió tras varios intentos"
        ) from error

    registrar_costo(respuesta)

    return extraer_texto(respuesta)


if __name__ == "__main__":
    try:
        print("Modelo:", MODELO)

        resultado = consultar_modelo(
            "¿Cuál es la capital de Chile?"
        )

        print("Respuesta:", resultado)

    except (
        ValueError,
        RuntimeError,
        requests.HTTPError
    ) as error:
        print("ERROR:", error)