
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from cprint import cprint


# ==========================================
# 1. CARGAR API KEY DESDE .ENV
# ==========================================

ruta_env = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(ruta_env, override=True)

api_key = os.getenv("GEMINI_API_KEY")
nombre_modelo = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not api_key:
    raise ValueError(
        "No se encontró GEMINI_API_KEY en el archivo .env"
    )


# ==========================================
# 2. DEFINIR PLANTILLA
# ==========================================

plantilla = PromptTemplate.from_template(
    "Estima quién tendría más posibilidades de ganar "
    "entre {tenista_1} y {tenista_2} "
    "en una superficie de {superficie}. "
    "Responde solamente con el nombre del favorito "
    "y un porcentaje aproximado. "
    "Aclara que es una estimación, no una "
    "probabilidad estadística calculada."
)


# ==========================================
# 3. CONFIGURAR GEMINI
# ==========================================

modelo = ChatGoogleGenerativeAI(
    model=nombre_modelo,
    google_api_key=api_key,
    temperature=0
)


# ==========================================
# 4. CREAR CADENA LANGCHAIN
# ==========================================

cadena_simple = (
    plantilla
    | modelo
    | StrOutputParser()
)


# ==========================================
# 5. DATOS DE ENTRADA
# ==========================================

datos = {
    "tenista_1": "Rafael Nadal",
    "tenista_2": "Roger Federer",
    "superficie": "arcilla"
}


# ==========================================
# 6. EJECUTAR
# ==========================================

try:
    prompt = plantilla.invoke(datos)

    cprint.ok("PROMPT GENERADO:")
    print(prompt.text)

    cprint.ok("RESPUESTA DE GEMINI:")

    respuesta = cadena_simple.invoke(datos)

    cprint.info(respuesta)

except Exception as error:
    mensaje = str(error)

    if "API_KEY_INVALID" in mensaje:
        cprint.err("ERROR: API Key de Gemini inválida.")

    elif "404" in mensaje or "NOT_FOUND" in mensaje:
        cprint.err("ERROR: Modelo Gemini no disponible.")

    else:
        cprint.err(f"ERROR: {mensaje}")
