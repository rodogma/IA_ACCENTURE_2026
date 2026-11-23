
import os
import logging
from pathlib import Path

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.tools import tool

from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)

from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)


# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)

# Buscar .env en la raíz del proyecto
RUTA_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_ENV = RUTA_PROYECTO / ".env"

load_dotenv(RUTA_ENV)

API_KEY = os.getenv("GEMINI_API_KEY")
NOMBRE_MODELO = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)


# ==========================================
# 2. HERRAMIENTAS DEL AGENTE
# ==========================================

@tool
def recomendar_maquinaria(tipo_trabajo: str) -> str:
    """
    Recomienda maquinaria de construcción
    según el tipo de trabajo solicitado.
    """

    trabajo = tipo_trabajo.lower()

    if "tierra" in trabajo or "excavación" in trabajo:
        return (
            "Para movimiento de tierra se recomienda "
            "utilizar excavadoras y cargadores frontales."
        )

    if "compactación" in trabajo or "compactar" in trabajo:
        return (
            "Para compactación se recomienda utilizar "
            "rodillos compactadores."
        )

    if "altura" in trabajo or "elevación" in trabajo:
        return (
            "Para trabajos en altura se recomienda "
            "utilizar plataformas elevadoras."
        )

    if "hormigón" in trabajo or "concreto" in trabajo:
        return (
            "Para trabajos con hormigón se recomienda "
            "utilizar mezcladoras y bombas de hormigón."
        )

    return (
        "Para recomendar maquinaria necesito "
        "conocer el tipo de trabajo."
    )


@tool
def recomendar_colores(color: str) -> str:
    """
    Recomienda colores que combinan con
    el color indicado por el usuario.
    """

    color = color.lower().strip()

    combinaciones = {
        "rojo": "blanco, negro, gris y beige",
        "azul": "blanco, gris, beige y naranja",
        "verde": "blanco, beige, marrón y gris",
        "amarillo": "gris, blanco, azul y negro",
        "negro": "blanco, gris, rojo y dorado",
        "blanco": "negro, azul, gris y beige",
    }

    if color in combinaciones:
        return (
            f"El color {color} combina bien con: "
            f"{combinaciones[color]}."
        )

    return (
        f"No tengo una combinación registrada "
        f"para el color {color}."
    )


# ==========================================
# 3. CREAR MODELO GEMINI
# ==========================================

def crear_modelo():

    if not API_KEY:
        raise ValueError(
            "No se encontró GEMINI_API_KEY. "
            "Revisa el archivo .env."
        )

    return ChatGoogleGenerativeAI(
        model=NOMBRE_MODELO,
        google_api_key=API_KEY,
        timeout=120,
        max_retries=1,
    )


# ==========================================
# 4. CREAR PROMPT DEL AGENTE
# ==========================================

def crear_prompt():

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Eres un asistente inteligente que "
                "responde siempre en español. "
                "Tienes herramientas para recomendar "
                "maquinaria de construcción y "
                "combinaciones de colores. "
                "Utiliza las herramientas cuando "
                "la consulta corresponda a sus funciones. "
                "Responde de forma clara y breve."
            ),

            (
                "human",
                "{entrada}"
            ),

            MessagesPlaceholder(
                variable_name="agent_scratchpad"
            ),
        ]
    )


# ==========================================
# 5. CONSTRUIR AGENTE
# ==========================================

def crear_ejecutor_agente():

    modelo = crear_modelo()

    herramientas = [
        recomendar_maquinaria,
        recomendar_colores,
    ]

    prompt = crear_prompt()

    agente = create_tool_calling_agent(
        llm=modelo,
        tools=herramientas,
        prompt=prompt,
    )

    ejecutor_agente = AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True,
        max_iterations=3,
        handle_parsing_errors=True,
    )

    return ejecutor_agente


# ==========================================
# 6. EJECUCIÓN SEGURA
# ==========================================

def consultar_agente(ejecutor, pregunta):

    print("\n" + "=" * 50)
    print("PREGUNTA:", pregunta)
    print("=" * 50)

    try:

        resultado = ejecutor.invoke(
            {"entrada": pregunta}
        )

        respuesta = resultado.get(
            "output",
            "El agente no generó una respuesta."
        )

        print("\nRESPUESTA DEL AGENTE:")
        print(respuesta)

        return respuesta

    except Exception as error:

        logger.error(
            "No se pudo ejecutar el agente: %s",
            error
        )

        print("\nNo fue posible obtener una respuesta.")
        print("Tipo de error:", type(error).__name__)
        print("Detalle:", error)

        return None


# ==========================================
# 7. PROGRAMA PRINCIPAL
# ==========================================

def main():

    print("\n======================================")
    print("BLOQUE 21 - AGENTE CON LANGCHAIN")
    print("======================================")

    print("\nModelo configurado:", NOMBRE_MODELO)

    # Comprobar herramienta local
    print("\nPRUEBA DE HERRAMIENTA LOCAL:")

    resultado_local = recomendar_maquinaria.invoke(
        {"tipo_trabajo": "movimiento de tierra"}
    )

    print(resultado_local)

    # Crear agente con Gemini
    try:

        print("\nCreando agente con Gemini...")

        ejecutor_agente = crear_ejecutor_agente()

    except Exception as error:

        print("\nNo se pudo crear el agente.")
        print("Error:", error)
        return

    # Consulta 1
    consultar_agente(
        ejecutor_agente,
        "¿Qué color combina con el rojo?"
    )

    # Consulta 2
    consultar_agente(
        ejecutor_agente,
        "¿Qué maquinaria recomiendas "
        "para movimiento de tierra?"
    )

    print("\n======================================")
    print("FIN DEL PROGRAMA")
    print("======================================")


if __name__ == "__main__":
    main()
