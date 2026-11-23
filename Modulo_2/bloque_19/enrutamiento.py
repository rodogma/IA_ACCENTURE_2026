
import os
import time

from dotenv import load_dotenv
from cprint import cprint

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    Runnable,
    RunnableBranch,
    RunnablePassthrough,
    RunnableLambda,
)

# ==========================================
# 1. CARGAR VARIABLES DE ENTORNO
# ==========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODELO = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

if not API_KEY:
    raise ValueError("No se encontró GEMINI_API_KEY en .env")


# ==========================================
# 2. CONFIGURAR GEMINI
# ==========================================

def crear_modelo(nombre):
    return ChatGoogleGenerativeAI(
        model=nombre,
        google_api_key=API_KEY,
        temperature=0,
        max_retries=2,
        timeout=30,
    )


# ==========================================
# 3. PLANTILLA DE CLASIFICACIÓN
# ==========================================

plantilla_clasificacion = PromptTemplate.from_template(
    "Clasifica el siguiente mensaje de soporte en una sola "
    "palabra: pregunta, queja o sugerencia. "
    "Responde solo con esa palabra.\n\n{mensaje}"
)


# ==========================================
# 4. CONSTRUIR CLASIFICADOR
# ==========================================

def construir_paso_clasificacion(modelo):
    return (
        plantilla_clasificacion
        | modelo
        | StrOutputParser()
        | RunnableLambda(lambda texto: texto.strip().lower())
    )


# ==========================================
# 5. CONSTRUIR CADENA DE ENRUTAMIENTO
# ==========================================

def construir_cadena_con_enrutamiento(
    paso_clasificacion,
    cadena_queja=None,
    cadena_sugerencia=None,
    cadena_pregunta=None,
):

    def convertir_a_runnable(cadena):
        if cadena is None:
            return RunnablePassthrough()

        if isinstance(cadena, Runnable):
            return cadena

        return RunnableLambda(cadena)

    paso_clasificacion = convertir_a_runnable(
        paso_clasificacion
    )

    cadena_queja = convertir_a_runnable(cadena_queja)
    cadena_sugerencia = convertir_a_runnable(cadena_sugerencia)
    cadena_pregunta = convertir_a_runnable(cadena_pregunta)

    bifurcacion = RunnableBranch(
        (
            lambda x: x["categoria"] == "queja",
            cadena_queja,
        ),
        (
            lambda x: x["categoria"] == "sugerencia",
            cadena_sugerencia,
        ),
        cadena_pregunta,
    )

    return (
        RunnablePassthrough.assign(
            categoria=paso_clasificacion
        )
        | bifurcacion
    )


# ==========================================
# 6. CREAR CADENAS DE RESPUESTA
# ==========================================

def crear_cadena_completa(modelo):

    cadena_pregunta = (
        PromptTemplate.from_template(
            "Responde esta pregunta técnica con precisión:\n\n"
            "{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )

    cadena_queja = (
        PromptTemplate.from_template(
            "Responde a esta queja con empatía, reconociendo "
            "el problema antes de ofrecer una solución:\n\n"
            "{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )

    cadena_sugerencia = (
        PromptTemplate.from_template(
            "Agradece esta sugerencia y explica cómo se "
            "evaluará dentro del producto:\n\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )

    paso_clasificacion = construir_paso_clasificacion(
        modelo
    )

    return construir_cadena_con_enrutamiento(
        paso_clasificacion=paso_clasificacion,
        cadena_queja=cadena_queja,
        cadena_sugerencia=cadena_sugerencia,
        cadena_pregunta=cadena_pregunta,
    )


# ==========================================
# 7. CONEXIÓN CON REINTENTOS Y MODELO ALTERNO
# ==========================================

def ejecutar_con_gemini(texto):

    modelos = list(dict.fromkeys([
        MODELO,
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
    ]))

    for nombre_modelo in modelos:

        print(f"\nProbando modelo: {nombre_modelo}")

        try:
            modelo = crear_modelo(nombre_modelo)
            cadena = crear_cadena_completa(modelo)

            for intento in range(1, 4):
                try:
                    resultado = cadena.invoke(
                        {"mensaje": texto}
                    )

                    print("\nConexión exitosa.")
                    print("Modelo:", nombre_modelo)

                    return resultado

                except Exception as error:
                    mensaje = str(error)

                    if (
                        "503" in mensaje
                        or "UNAVAILABLE" in mensaje
                        or "429" in mensaje
                        or "RESOURCE_EXHAUSTED" in mensaje
                    ):
                        print(
                            f"Error temporal. "
                            f"Intento {intento}/3"
                        )

                        if intento < 3:
                            time.sleep(3 * intento)
                        else:
                            print(
                                "Probando otro modelo..."
                            )
                    else:
                        print(
                            "Error de conexión:",
                            error
                        )
                        return None

        except Exception as error:
            print("Error al configurar el modelo:", error)
            return None

    print("\nNo se pudo obtener respuesta de Gemini.")
    return None


# ==========================================
# 8. EJECUCIÓN PRINCIPAL
# ==========================================

if __name__ == "__main__":

    texto = "Pueden aplicar una fuente más grande?"

    print("\n================================")
    print("SISTEMA DE SOPORTE CON LANGCHAIN")
    print("================================")

    print("\nMensaje recibido:", texto)

    resultado = ejecutar_con_gemini(texto)

    if resultado is not None:
        print("\nRespuesta:")
        cprint.fatal(resultado)
    else:
        print(
            "\nNo fue posible completar la solicitud."
        )
