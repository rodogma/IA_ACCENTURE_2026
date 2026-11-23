
import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_paso_clasificacion,
)


# ==========================================
# 1. CONFIGURACION
# ==========================================

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ_PROYECTO / ".env")

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
MODELO = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

RESPUESTA_GENERICA = (
    "Gracias por tu mensaje. "
    "Un miembro de nuestro equipo te responderá pronto."
)


# ==========================================
# 2. RESPUESTA DE EMERGENCIA
# ==========================================

respuesta_generica = RunnableLambda(
    lambda datos: RESPUESTA_GENERICA
)


# ==========================================
# 3. SIMULAR ERRORES
# ==========================================

def fallar_a_proposito(datos):
    raise RuntimeError("Error de red simulado")


cadena_rota = RunnableLambda(fallar_a_proposito)

cadena_secundaria_rota = RunnableLambda(
    fallar_a_proposito
)

cadena_doble_segura = cadena_rota.with_fallbacks(
    [
        cadena_secundaria_rota,
        respuesta_generica,
    ]
)


# ==========================================
# 4. CREAR MODELO
# ==========================================

def crear_modelo(timeout=15):

    if not API_KEY:
        raise ValueError(
            "Falta GEMINI_API_KEY en el archivo .env"
        )

    return ChatGoogleGenerativeAI(
        model=MODELO,
        google_api_key=API_KEY,
        timeout=timeout,
        max_retries=0,
    )


# ==========================================
# 5. CREAR CADENAS DE RESPUESTA
# ==========================================

def crear_cadena_respuesta(instruccion, modelo):

    plantilla = PromptTemplate.from_template(
        instruccion + "\n\n{mensaje}"
    )

    return (
        plantilla
        | modelo
        | StrOutputParser()
    )


# ==========================================
# 6. CONSTRUIR ENRUTAMIENTO REAL
# ==========================================

def crear_enrutamiento_seguro():

    modelo = crear_modelo(timeout=15)

    cadena_queja = crear_cadena_respuesta(
        "Responde a esta queja con empatía "
        "y ofrece una solución:",
        modelo,
    )

    cadena_pregunta = crear_cadena_respuesta(
        "Responde claramente esta pregunta "
        "de soporte técnico:",
        modelo,
    )

    cadena_sugerencia = crear_cadena_respuesta(
        "Agradece esta sugerencia y explica "
        "que será evaluada:",
        modelo,
    )

    # Si falla la respuesta de Gemini,
    # devolver una respuesta generica.
    cadena_queja_segura = cadena_queja.with_fallbacks(
        [respuesta_generica]
    )

    cadena_pregunta_segura = cadena_pregunta.with_fallbacks(
        [respuesta_generica]
    )

    cadena_sugerencia_segura = (
        cadena_sugerencia.with_fallbacks(
            [respuesta_generica]
        )
    )

    # Clasificacion real mediante Gemini
    clasificador = construir_paso_clasificacion(
        modelo
    )

    # Si falla la clasificacion,
    # usar "pregunta" como ruta por defecto.
    clasificador_seguro = clasificador.with_fallbacks(
        [RunnableLambda(lambda datos: "pregunta")]
    )

    return construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificador_seguro,
        cadena_queja=cadena_queja_segura,
        cadena_pregunta=cadena_pregunta_segura,
        cadena_sugerencia=cadena_sugerencia_segura,
    )


# ==========================================
# 7. PROCESAR MENSAJE
# ==========================================

def procesar_mensaje_seguro(mensaje):

    print("\nMensaje recibido:", mensaje, flush=True)
    print("Modelo:", MODELO, flush=True)
    print(
        "Clasificando y generando respuesta...",
        flush=True
    )

    try:
        cadena = crear_enrutamiento_seguro()

        resultado = cadena.invoke(
            {"mensaje": mensaje}
        )

        print("Procesamiento finalizado.", flush=True)

        return resultado

    except Exception as error:

        logger.error(
            "Error procesando mensaje: %s",
            error
        )

        return RESPUESTA_GENERICA


# ==========================================
# 8. PROGRAMA PRINCIPAL
# ==========================================

if __name__ == "__main__":

    print("\n================================")
    print("MANEJO DE ERRORES CON LANGCHAIN")
    print("================================", flush=True)

    # PRUEBA 1: SIN GEMINI
    print("\nPRUEBA 1: FALLBACK SIMULADO", flush=True)

    resultado = cadena_doble_segura.invoke(
        {"mensaje": "La aplicación se cierra sola"}
    )

    print("Respuesta:", resultado, flush=True)

    # PRUEBA 2: CON GEMINI
    print("\nPRUEBA 2: ENRUTAMIENTO REAL", flush=True)

    resultado = procesar_mensaje_seguro(
        "Pueden aplicar una fuente más grande?"
    )

    print("\nRespuesta final:")
    print(resultado, flush=True)

    print("\nFIN DEL PROGRAMA", flush=True)
