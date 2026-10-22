
import os
import json
import re
import requests

from pathlib import Path
from dotenv import load_dotenv


# =====================================================
# 1. CONFIGURACIÓN DEL PROYECTO
# =====================================================

# Raíz del proyecto IA_ACCENTURE_2026
RAIZ = Path(__file__).resolve().parents[3]

# Ubicación del archivo .env
RUTA_ENV = RAIZ / ".env"

# Cargar variables de entorno
if not RUTA_ENV.is_file():
    raise FileNotFoundError(
        f"No se encontró el archivo .env en: {RUTA_ENV}"
    )

load_dotenv(dotenv_path=RUTA_ENV)

# Obtener credencial
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "No se encontró GEMINI_API_KEY en el archivo .env"
    )

# Modelo de Gemini
MODELO = "gemini-3.5-flash-lite"


# =====================================================
# 2. ARMAR PETICIÓN
# =====================================================

def armar_peticion(
    pregunta,
    system_instruction=None,
    response_schema=None
):

    # Validar entrada
    if not isinstance(pregunta, str):
        raise TypeError(
            "La pregunta debe ser una cadena de texto."
        )

    if not pregunta.strip():
        raise ValueError(
            "La pregunta no puede estar vacía."
        )

    # Construir URL
    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{MODELO}:generateContent"
    )

    # Cuerpo principal
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": pregunta}
                ]
            }
        ]
    }

    # Agregar instrucciones de sistema
    if system_instruction:
        body["systemInstruction"] = {
            "parts": [
                {"text": system_instruction}
            ]
        }

    # Configurar respuesta JSON
    generation_config = {
        "responseMimeType": "application/json",
        "temperature": 0.1
    }

    # Incorporar esquema opcional
    if response_schema is not None:
        generation_config["responseSchema"] = response_schema

    body["generationConfig"] = generation_config

    # Configurar encabezados
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    return url, body, headers


# =====================================================
# 3. ENVIAR PETICIÓN
# =====================================================

def enviar_peticion(url, body, headers):

    respuesta = requests.post(
        url,
        json=body,
        headers=headers,
        timeout=60
    )

    # Detectar errores HTTP
    respuesta.raise_for_status()

    # Convertir JSON a diccionario Python
    return respuesta.json()


# =====================================================
# 4. EXTRAER TEXTO
# =====================================================

def extraer_texto(datos):

    try:
        partes = datos["candidates"][0]["content"]["parts"]

        texto = "\n".join(
            parte["text"]
            for parte in partes
            if "text" in parte
        )

        if not texto.strip():
            raise ValueError(
                "Gemini devolvió una respuesta sin texto."
            )

        return texto

    except (KeyError, IndexError, TypeError) as error:

        raise ValueError(
            "No se pudo extraer el texto de Gemini."
        ) from error


# =====================================================
# 5. PARSEAR RESPUESTA JSON
# =====================================================

def parsear_respuesta_json(texto):

    if not isinstance(texto, str):
        raise TypeError(
            "La respuesta debe ser una cadena de texto."
        )

    # Eliminar espacios innecesarios
    texto = texto.strip()

    # Eliminar posibles bloques Markdown
    texto = re.sub(
        r"^```(?:json)?\s*",
        "",
        texto,
        flags=re.IGNORECASE
    )

    texto = re.sub(
        r"\s*```$",
        "",
        texto
    )

    try:
        datos = json.loads(texto)

    except json.JSONDecodeError as error:

        raise ValueError(
            f"La respuesta no contiene JSON válido: {error}"
        ) from error

    # Validar que sea un objeto JSON
    if not isinstance(datos, dict):
        raise ValueError(
            "La respuesta JSON debe ser un objeto."
        )

    return datos


# =====================================================
# 6. PRUEBA INDIVIDUAL
# =====================================================

if __name__ == "__main__":

    try:

        pregunta = (
            "Clasifica el sentimiento de esta frase: "
            "El servicio fue excelente."
        )

        instrucciones = (
            "Responde solamente con un objeto JSON "
            "que contenga las claves 'sentimiento' "
            "y 'confianza'. "
            "El sentimiento debe ser positivo, "
            "negativo o neutro. "
            "La confianza debe ser un número entre 0 y 1."
        )

        esquema = {
            "type": "OBJECT",
            "properties": {
                "sentimiento": {
                    "type": "STRING"
                },
                "confianza": {
                    "type": "NUMBER"
                }
            },
            "required": [
                "sentimiento",
                "confianza"
            ]
        }

        # Preparar petición
        url, body, headers = armar_peticion(
            pregunta,
            instrucciones,
            esquema
        )

        # Enviar petición
        respuesta = enviar_peticion(
            url,
            body,
            headers
        )

        # Extraer texto
        texto = extraer_texto(respuesta)

        # Convertir a diccionario Python
        datos = parsear_respuesta_json(texto)

        print("\nRespuesta JSON de Gemini:")
        print(json.dumps(
            datos,
            indent=2,
            ensure_ascii=False
        ))

    except requests.exceptions.Timeout:
        print(
            "Error: Gemini tardó demasiado en responder."
        )

    except requests.exceptions.HTTPError as error:
        print(
            f"Error HTTP: {error.response.status_code}"
        )
        print("Detalle:", error.response.text)

    except requests.exceptions.RequestException as error:
        print("Error de conexión:", error)

    except (ValueError, TypeError) as error:
        print("Error de validación:", error)
