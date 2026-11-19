
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# Buscar .env en la carpeta actual y carpetas superiores
BASE_DIR = Path(__file__).resolve().parent

for carpeta in [BASE_DIR, *BASE_DIR.parents]:
    ruta_env = carpeta / ".env"

    if ruta_env.is_file():
        load_dotenv(dotenv_path=ruta_env, override=True)
        print(f"Archivo .env encontrado: {ruta_env}")
        break
else:
    print("ADVERTENCIA: No se encontró el archivo .env")


def consultar_modelo(consulta: str) -> str:
    """Consulta Gemini y devuelve la respuesta como texto."""

    api_key = os.getenv("GEMINI_API_KEY")
    modelo = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        raise ValueError(
            "No se encontró GEMINI_API_KEY. "
            "Revisa la ubicación de tu archivo .env."
        )

    cliente = genai.Client(api_key=api_key)

    try:
        respuesta = cliente.models.generate_content(
            model=modelo,
            contents=consulta,
            config={
                "temperature": 0
            }
        )

        return respuesta.text or ""

    finally:
        cliente.close()


if __name__ == "__main__":
    try:
        print("Verificando configuración de Gemini...")

        print(
            "API KEY:",
            "CONFIGURADA" if os.getenv("GEMINI_API_KEY")
            else "NO CONFIGURADA"
        )

        print(
            "MODELO:",
            os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        )

        pregunta = "¿Qué es Python?"
        respuesta = consultar_modelo(pregunta)

        print("\nPregunta:", pregunta)
        print("Respuesta Gemini:", respuesta)

    except Exception as error:
        print("\nERROR:", error)
