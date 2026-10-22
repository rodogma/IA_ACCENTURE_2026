
import os
import requests
from pathlib import Path
from dotenv import load_dotenv


# Cargar el archivo .env desde la raíz del proyecto
ruta_env = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ruta_env)


def obtener_dato_de_prueba(pregunta):

    # 1. Validar la pregunta
    if not isinstance(pregunta, str):
        raise TypeError(
            "La pregunta debe ser una cadena de texto."
        )

    if not pregunta.strip():
        raise ValueError(
            "La pregunta no puede estar vacía."
        )

    # 2. Obtener clave API
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "No se encontró GEMINI_API_KEY en el archivo .env"
        )

    # 3. Seleccionar modelo
    modelo = "gemini-3.5-flash-lite"

    # 4. Construir URL
    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{modelo}:generateContent"
    )

    # 5. Preparar cuerpo de la petición
    body = {
        "contents": [
            {
                "parts": [
                    {"text": pregunta}
                ]
            }
        ]
    }

    # 6. Configurar encabezados
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    # 7. Enviar petición HTTP
    respuesta = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=60
    )

    # 8. Comprobar errores HTTP
    respuesta.raise_for_status()

    # 9. Convertir JSON en diccionario
    datos = respuesta.json()

    # 10. Extraer el texto
    try:
        texto = datos["candidates"][0]["content"]["parts"][0]["text"]

    except (KeyError, IndexError, TypeError) as error:
        raise ValueError(
            "Gemini no devolvió una respuesta de texto válida."
        ) from error

    # 11. Devolver el resultado
    return texto
