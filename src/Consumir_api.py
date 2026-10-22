

import os
import requests
from dotenv import load_dotenv
from pathlib import Path


# 1. Cargar el archivo .env desde la raíz del proyecto
ruta_env = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ruta_env)


# 2. Crear función que consulta la API de Gemini
def obtener_dato_de_prueba(pregunta):

    # Obtener la clave API desde el entorno
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "No se encontró GEMINI_API_KEY en el archivo .env"
        )

    # Seleccionar el modelo de Gemini
    modelo = "gemini-3.5-flash-lite"

    # Construir URL del endpoint
    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{modelo}:generateContent"
    )

    # 3. Preparar el cuerpo de la petición
    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": pregunta
                    }
                ]
            }
        ]
    }

    # 4. Enviar petición HTTP POST
    respuesta = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        },
        json=body,
        timeout=60
    )

    # 5. Verificar si hubo errores HTTP
    respuesta.raise_for_status()

    # 6. Convertir JSON a diccionario Python
    datos = respuesta.json()

    # 7. Extraer el texto generado
    texto = datos["candidates"][0]["content"]["parts"][0]["text"]

    # 8. Devolver el resultado
    return texto


# 9. Prueba de funcionamiento
if __name__ == "__main__":

    try:
        resultado = obtener_dato_de_prueba(
            "¿Qué es la inteligencia artificial y para qué sirve?"
        )

        print("Respuesta de Gemini:")
        print(resultado)

    except requests.exceptions.Timeout:
        print("Error: la API tardó demasiado en responder.")

    except requests.exceptions.RequestException as error:
        print("Error en la petición:", error)

    except (KeyError, IndexError, TypeError) as error:
        print("Error al procesar el JSON:", error)

    except ValueError as error:
        print("Error de configuración:", error)
