
import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from cprint import cprint


# ==========================================
# 1. CARGAR ARCHIVO .ENV
# ==========================================

ruta_env = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(ruta_env, override=True)

api_key = os.getenv("GEMINI_API_KEY")
nombre_modelo = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not api_key:
    raise ValueError(
        f"No se encontró GEMINI_API_KEY en {ruta_env}"
    )

print("API Key cargada:", bool(api_key))
print("Modelo:", nombre_modelo)


# ==========================================
# 2. DEFINICIÓN DE LA PLANTILLA
# ==========================================

plantilla = PromptTemplate.from_template(
    "Probabilidades de que {tenista_1} le gane a {tenista_2}"
    " en una superficie de {superficie}."
    " Dame respuesta corta, solo quién gana y un"
    " porcentaje aproximado de probabilidad."
)


# ==========================================
# 3. DATOS DE LOS TENISTAS
# ==========================================

datos = {
    "tenista_1": "Rafael Nadal",
    "tenista_2": "Roger Federer",
    "superficie": "arcilla"
}


# ==========================================
# 4. INVOCAR LA PLANTILLA
# ==========================================

prompt = plantilla.invoke(datos)

cprint.ok("PROMPT GENERADO:")
print(prompt.text)


# ==========================================
# 5. CONFIGURAR GEMINI
# ==========================================

modelo = ChatGoogleGenerativeAI(
    model=nombre_modelo,
    google_api_key=api_key,
    temperature=0
)


# ==========================================
# 6. INVOCAR MODELO DIRECTAMENTE
# ==========================================

respuesta = modelo.invoke(prompt)

cprint.ok("RESPUESTA DIRECTA:")
cprint.info(respuesta.content)


# ==========================================
# 7. CREAR CADENA SIMPLE LANGCHAIN
# ==========================================

cadena_simple = plantilla | modelo


# ==========================================
# 8. EJECUTAR CADENA
# ==========================================

respuesta = cadena_simple.invoke(datos)

cprint.ok("RESPUESTA CON CADENA:")
cprint.info(respuesta.content)
