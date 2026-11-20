
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


# ==========================================
# 1. CONSTRUIR LA CADENA
# ==========================================

def construir_cadena(modelo):

    parser = StrOutputParser()

    # PASO 1: CLASIFICAR EL INCIDENTE
    plantilla_clasificar = PromptTemplate.from_template(
        "Eres un analista de soporte informático.\n"
        "Analiza la siguiente solicitud:\n\n"
        "{texto}\n\n"
        "Identifica:\n"
        "1. Categoría del problema.\n"
        "2. Prioridad: baja, media o alta.\n"
        "3. Descripción breve del incidente.\n"
        "No inventes información."
    )

    paso_clasificar = (
        plantilla_clasificar
        | modelo
        | parser
    )

    # PASO 2: REDACTAR UNA RESPUESTA
    plantilla_redactar = PromptTemplate.from_template(
        "Eres un especialista de soporte técnico.\n"
        "Utiliza la siguiente clasificación:\n\n"
        "{clasificacion}\n\n"
        "Redacta una respuesta profesional que incluya:\n"
        "1. Reconocimiento del problema.\n"
        "2. Recomendaciones iniciales seguras.\n"
        "3. Cuándo contactar al equipo de TI.\n"
        "No solicites contraseñas ni datos sensibles."
    )

    paso_redactar = (
        plantilla_redactar
        | modelo
        | parser
    )

    # PASO 3: REVISAR Y MEJORAR
    plantilla_revisar = PromptTemplate.from_template(
        "Eres un revisor de calidad de soporte.\n"
        "Revisa esta respuesta:\n\n"
        "{respuesta}\n\n"
        "Mejora su claridad, ortografía y tono.\n"
        "Usa lenguaje sencillo y profesional.\n"
        "Organiza el resultado en Markdown.\n"
        "No agregues información no confirmada.\n"
        "Devuelve solamente la respuesta final."
    )

    paso_revisar = (
        plantilla_revisar
        | modelo
        | parser
    )

    # ENCADENAMIENTO DE LOS TRES PASOS
    cadena = (
        paso_clasificar
        | (lambda clasificacion: {
            "clasificacion": clasificacion
        })
        | paso_redactar
        | (lambda respuesta: {
            "respuesta": respuesta
        })
        | paso_revisar
    )

    return cadena


# ==========================================
# 2. CONFIGURAR GEMINI
# ==========================================

def main():

    ruta_env = (
        Path(__file__).resolve().parents[2] / ".env"
    )

    load_dotenv(ruta_env, override=True)

    api_key = os.getenv("GEMINI_API_KEY")
    nombre_modelo = os.getenv(
        "GEMINI_MODEL", "gemini-2.5-flash"
    )

    if not api_key:
        raise ValueError(
            "No se encontró GEMINI_API_KEY en .env"
        )

    modelo = ChatGoogleGenerativeAI(
        model=nombre_modelo,
        google_api_key=api_key,
        temperature=0,
        max_retries=1
    )

    # ======================================
    # 3. CASO REAL DE ENTRADA
    # ======================================

    solicitud = (
        "Soy empleado del área de finanzas. "
        "Desde esta mañana no puedo ingresar "
        "a mi correo corporativo. "
        "Al intentar iniciar sesión aparece "
        "un mensaje indicando que mi cuenta "
        "está bloqueada. "
        "Necesito revisar correos importantes "
        "para entregar un informe financiero "
        "antes de finalizar la jornada."
    )

    # ======================================
    # 4. EJECUTAR CADENA
    # ======================================

    cadena = construir_cadena(modelo)

    print("\nINICIANDO ANÁLISIS DE SOPORTE...\n")

    resultado = cadena.invoke({
        "texto": solicitud
    })

    print("RESULTADO FINAL:")
    print("=" * 50)
    print(resultado)
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()

    except Exception as error:
        mensaje = str(error)

        if "API_KEY_INVALID" in mensaje:
            print("ERROR: API Key de Gemini inválida.")

        elif "429" in mensaje:
            print("ERROR: Límite de solicitudes alcanzado.")

        else:
            print(
                f"ERROR: {type(error).__name__}: "
                f"{mensaje}"
            )
