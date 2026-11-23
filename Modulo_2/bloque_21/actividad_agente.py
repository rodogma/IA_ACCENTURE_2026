
import os
import time
import logging
from pathlib import Path

from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)


# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)

RUTA_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_ENV = RUTA_PROYECTO / ".env"

load_dotenv(RUTA_ENV)

API_KEY = os.getenv("GEMINI_API_KEY")
NOMBRE_MODELO = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite",
)

MAX_INTENTOS = 3

if not API_KEY:
    raise ValueError(
        "No se encontró GEMINI_API_KEY. "
        "Revisa el archivo .env."
    )


# ==========================================
# 2. HERRAMIENTA 1: RECOMENDAR MAQUINARIA
# ==========================================

@tool
def recomendar_maquinaria(tipo_trabajo: str) -> str:
    """
    Recomienda maquinaria para una obra.

    Usar cuando el usuario pregunta qué máquina
    necesita para movimiento de tierra, excavación,
    compactación o trabajos en altura.

    No usar para calcular precios de arriendo.
    """

    try:
        trabajo = tipo_trabajo.lower().strip()

        if "tierra" in trabajo or "excav" in trabajo:
            return (
                "Para movimiento de tierra o excavación "
                "se recomienda una excavadora."
            )

        if "compact" in trabajo:
            return (
                "Para compactar terreno se recomienda "
                "un rodillo compactador."
            )

        if "altura" in trabajo or "elev" in trabajo:
            return (
                "Para trabajos en altura se recomienda "
                "una plataforma elevadora."
            )

        return (
            "No tengo una recomendación específica. "
            "Indica el tipo de trabajo de construcción."
        )

    except Exception as error:
        logger.exception(
            "Error en recomendar_maquinaria"
        )
        return (
            "No fue posible recomendar maquinaria. "
            f"Detalle: {error}"
        )


# ==========================================
# 3. HERRAMIENTA 2: CALCULAR ARRIENDO
# ==========================================

@tool
def calcular_costo_arriendo(
    tipo_maquina: str,
    horas: float,
) -> str:
    """
    Calcula el costo estimado de arrendar maquinaria.

    Usar cuando el usuario pregunta cuánto cuesta
    arrendar una excavadora, rodillo compactador
    o plataforma elevadora por cierta cantidad
    de horas.

    No usar para recomendar qué maquinaria necesita.
    """

    try:
        tarifas = {
            "excavadora": 45000,
            "rodillo compactador": 30000,
            "plataforma elevadora": 25000,
        }

        maquina = tipo_maquina.lower().strip()

        if maquina not in tarifas:
            return (
                f"No existe una tarifa registrada "
                f"para '{tipo_maquina}'."
            )

        if horas <= 0:
            return (
                "La cantidad de horas debe "
                "ser mayor que cero."
            )

        tarifa_hora = tarifas[maquina]
        costo_total = tarifa_hora * horas

        return (
            f"El arriendo de una {maquina} "
            f"durante {horas:g} horas cuesta "
            f"aproximadamente ${costo_total:,.0f} CLP. "
            "Tarifa ficticia utilizada para "
            "esta actividad académica."
        )

    except Exception as error:
        logger.exception(
            "Error en calcular_costo_arriendo"
        )
        return (
            "No fue posible calcular el arriendo. "
            f"Detalle: {error}"
        )


# ==========================================
# 4. CREAR MODELO GEMINI
# ==========================================

def crear_modelo():

    return ChatGoogleGenerativeAI(
        model=NOMBRE_MODELO,
        google_api_key=API_KEY,
        timeout=120,
        max_retries=1,
    )


# ==========================================
# 5. CREAR PROMPT
# ==========================================

def crear_prompt():

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Eres un asistente especializado en "
                "maquinaria de construcción. "
                "Responde siempre en español. "

                "Dispones de dos herramientas: "

                "1. recomendar_maquinaria: "
                "úsala únicamente cuando el usuario "
                "necesite saber qué maquinaria utilizar "
                "para realizar un trabajo. "

                "2. calcular_costo_arriendo: "
                "úsala únicamente cuando el usuario "
                "solicite calcular el precio de arriendo "
                "de una máquina. "

                "Para saludos o preguntas generales, "
                "responde directamente sin herramientas. "

                "Si una herramienta devuelve información, "
                "utiliza su resultado para responder. "

                "Las tarifas son ficticias y no "
                "representan cotizaciones reales. "

                "No inventes precios ni datos."
            ),
            (
                "human",
                "{entrada}",
            ),
            MessagesPlaceholder(
                variable_name="agent_scratchpad"
            ),
        ]
    )


# ==========================================
# 6. CONSTRUIR AGENTE
# ==========================================

def crear_ejecutor_agente():

    herramientas = [
        recomendar_maquinaria,
        calcular_costo_arriendo,
    ]

    modelo = crear_modelo()
    prompt = crear_prompt()

    agente = create_tool_calling_agent(
        llm=modelo,
        tools=herramientas,
        prompt=prompt,
    )

    ejecutor = AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True,
        return_intermediate_steps=True,
        max_iterations=3,
        handle_parsing_errors=True,
    )

    return ejecutor


# ==========================================
# 7. LIMPIAR RESPUESTAS DE GEMINI
# ==========================================

def limpiar_respuesta(respuesta):

    if isinstance(respuesta, str):
        return respuesta

    if isinstance(respuesta, list):
        textos = []

        for bloque in respuesta:
            if isinstance(bloque, dict):
                if bloque.get("type") == "text":
                    textos.append(
                        bloque.get("text", "")
                    )

        return " ".join(textos)

    return str(respuesta)


# ==========================================
# 8. DETECTAR ERRORES TEMPORALES
# ==========================================

def es_error_temporal(error):

    detalle = str(error).lower()
    nombre = type(error).__name__.lower()

    indicadores = [
        "503",
        "unavailable",
        "high demand",
        "readtimeout",
        "timed out",
        "timeout",
        "429",
        "resource_exhausted",
    ]

    return any(
        indicador in detalle or indicador in nombre
        for indicador in indicadores
    )


# ==========================================
# 9. EJECUTAR CON REINTENTOS
# ==========================================

def invocar_con_reintentos(ejecutor, pregunta):

    for intento in range(1, MAX_INTENTOS + 1):

        try:
            print(
                f"\nIntento {intento}/{MAX_INTENTOS}",
                flush=True,
            )

            resultado = ejecutor.invoke({
                "entrada": pregunta
            })

            return resultado

        except Exception as error:

            if not es_error_temporal(error):
                print(
                    "\nERROR NO RECUPERABLE:",
                    type(error).__name__,
                    error,
                )
                return None

            if intento == MAX_INTENTOS:
                print(
                    "\nGemini continúa sin responder."
                )
                print(
                    "Último error:",
                    type(error).__name__,
                    error,
                )
                return None

            espera = 10 * intento

            print(
                "\nGemini está saturado o "
                "la conexión tardó demasiado."
            )

            print(
                f"Reintentando en {espera} segundos..."
            )

            time.sleep(espera)

    return None


# ==========================================
# 10. VALIDAR HERRAMIENTAS
# ==========================================

def probar_agente(
    ejecutor,
    pregunta,
    herramienta_esperada,
):

    print("\n" + "=" * 60)
    print("PREGUNTA:", pregunta)
    print("=" * 60)

    resultado = invocar_con_reintentos(
        ejecutor,
        pregunta,
    )

    if resultado is None:
        print(
            "\nVALIDACIÓN: NO COMPLETADA "
            "POR ERROR DE LA API"
        )
        return "ERROR_API"

    pasos = resultado.get(
        "intermediate_steps",
        [],
    )

    herramientas_usadas = [
        accion.tool
        for accion, observacion in pasos
    ]

    print("\nHERRAMIENTAS UTILIZADAS:")
    print(herramientas_usadas)

    print("\nRESPUESTA FINAL:")
    print(
        limpiar_respuesta(
            resultado.get("output", "")
        )
    )

    if herramienta_esperada is None:
        correcto = herramientas_usadas == []
    else:
        correcto = herramientas_usadas == [
            herramienta_esperada
        ]

    if correcto:
        print("\nVALIDACIÓN: APROBADA")
        return "APROBADA"

    print("\nVALIDACIÓN: FALLIDA")
    print(
        "Herramienta esperada:",
        herramienta_esperada,
    )

    return "FALLIDA"


# ==========================================
# 11. PROGRAMA PRINCIPAL
# ==========================================

def main():

    print("\n========================================")
    print("BLOQUE 21 - ACTIVIDAD FINAL")
    print("AGENTE CON DOS HERRAMIENTAS")
    print("========================================")

    print("\nModelo:", NOMBRE_MODELO)

    ejecutor = crear_ejecutor_agente()

    # PRUEBA 1
    prueba_1 = probar_agente(
        ejecutor,
        "¿Qué maquinaria necesito para "
        "realizar movimiento de tierra?",
        "recomendar_maquinaria",
    )

    # PRUEBA 2
    prueba_2 = probar_agente(
        ejecutor,
        "¿Cuánto cuesta arrendar una "
        "excavadora durante 8 horas?",
        "calcular_costo_arriendo",
    )

    # PRUEBA 3
    prueba_3 = probar_agente(
        ejecutor,
        "Hola, buenos días.",
        None,
    )

    print("\n========================================")
    print("RESUMEN FINAL")
    print("========================================")

    print("Prueba 1:", prueba_1)
    print("Prueba 2:", prueba_2)
    print("Prueba 3:", prueba_3)

    if all(
        estado == "APROBADA"
        for estado in [
            prueba_1,
            prueba_2,
            prueba_3,
        ]
    ):
        print(
            "\nACTIVIDAD COMPLETADA CORRECTAMENTE"
        )
    else:
        print(
            "\nACTIVIDAD PENDIENTE DE VALIDACIÓN"
        )


if __name__ == "__main__":
    main()
