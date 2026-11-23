
import logging

from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableBranch,
    RunnablePassthrough,
)

# ==========================================
# 1. CONFIGURAR LOGGING
# ==========================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==========================================
# 2. CONVERTIR A RUNNABLE
# ==========================================

def convertir_a_runnable(cadena):

    if cadena is None:
        return RunnablePassthrough()

    if isinstance(cadena, Runnable):
        return cadena

    return RunnableLambda(cadena)


# ==========================================
# 3. CLASIFICAR MENSAJES
# ==========================================

plantilla_clasificacion = PromptTemplate.from_template(
    "Clasifica el siguiente mensaje de soporte "
    "en una sola categoría: pregunta, queja o "
    "sugerencia. Responde solamente con una "
    "de esas palabras.\n\n{mensaje}"
)


def construir_paso_clasificacion(modelo):

    modelo = convertir_a_runnable(modelo)

    return (
        plantilla_clasificacion
        | modelo
        | StrOutputParser()
        | RunnableLambda(
            lambda texto: texto.strip().lower()
        )
    )


# ==========================================
# 4. ENRUTAMIENTO
# ==========================================

def construir_cadena_con_enrutamiento(
    paso_clasificacion,
    cadena_queja=None,
    cadena_sugerencia=None,
    cadena_pregunta=None,
):

    paso_clasificacion = convertir_a_runnable(
        paso_clasificacion
    )

    cadena_queja = convertir_a_runnable(
        cadena_queja
    )

    cadena_sugerencia = convertir_a_runnable(
        cadena_sugerencia
    )

    cadena_pregunta = convertir_a_runnable(
        cadena_pregunta
    )

    rutas = RunnableBranch(
        (
            lambda datos: datos["categoria"] == "queja",
            cadena_queja,
        ),
        (
            lambda datos: datos["categoria"] == "sugerencia",
            cadena_sugerencia,
        ),
        cadena_pregunta,
    )

    return (
        RunnablePassthrough.assign(
            categoria=paso_clasificacion
        )
        | rutas
    )


# ==========================================
# 5. FALLBACK PARA QUEJAS
# ==========================================

def construir_cadena_queja_segura(cadena_queja):

    cadena_queja = convertir_a_runnable(
        cadena_queja
    )

    respuesta_respaldo = RunnableLambda(
        lambda datos: (
            "Lamentamos los inconvenientes que estás "
            "experimentando. Nuestro equipo de soporte "
            "revisará tu caso y te ayudará a encontrar "
            "una solución."
        )
    )

    return cadena_queja.with_fallbacks(
        [respuesta_respaldo]
    )


# ==========================================
# 6. PROCESAMIENTO SEGURO
# ==========================================

def procesar_mensaje_seguro(cadena, mensaje):

    try:
        return cadena.invoke(
            {"mensaje": mensaje}
        )

    except Exception as error:

        logger.error(
            "Error procesando mensaje: %s",
            error
        )

        return (
            "No pudimos procesar tu mensaje en este "
            "momento. Intenta de nuevo más tarde."
        )


# ==========================================
# 7. DEMOSTRACION SIN GEMINI
# ==========================================

def clasificar_demo(datos):

    mensaje = datos["mensaje"].lower()

    if any(
        palabra in mensaje
        for palabra in [
            "no funciona",
            "error",
            "falla",
            "molesto",
        ]
    ):
        return "queja"

    if any(
        palabra in mensaje
        for palabra in [
            "podrían",
            "pueden aplicar",
            "sugiero",
            "deberían",
        ]
    ):
        return "sugerencia"

    return "pregunta"


def responder_queja(datos):

    return (
        "Lamentamos el inconveniente. "
        "Nuestro equipo revisará tu problema."
    )


def responder_sugerencia(datos):

    return (
        "Gracias por tu sugerencia. "
        "La tendremos en cuenta para mejorar "
        "nuestro servicio."
    )


def responder_pregunta(datos):

    return (
        "Gracias por tu pregunta. "
        "Nuestro equipo te ayudará a resolverla."
    )


def crear_cadena_demo():

    cadena_queja_segura = (
        construir_cadena_queja_segura(
            RunnableLambda(responder_queja)
        )
    )

    return construir_cadena_con_enrutamiento(
        paso_clasificacion=RunnableLambda(
            clasificar_demo
        ),
        cadena_queja=cadena_queja_segura,
        cadena_sugerencia=RunnableLambda(
            responder_sugerencia
        ),
        cadena_pregunta=RunnableLambda(
            responder_pregunta
        ),
    )


# ==========================================
# 8. EJECUTAR ACTIVIDAD
# ==========================================

if __name__ == "__main__":

    print("\n================================")
    print("BLOQUE 20 - ACTIVIDAD ORQUESTACION")
    print("================================")

    cadena = crear_cadena_demo()

    mensajes = [
        "La aplicación no funciona",
        "¿Cómo cambio mi contraseña?",
        "Podrían aumentar el tamaño de la fuente",
    ]

    for mensaje in mensajes:

        print("\nMensaje:", mensaje)

        resultado = procesar_mensaje_seguro(
            cadena,
            mensaje
        )

        print("Respuesta:", resultado)

    print("\nFIN DE LA ACTIVIDAD")
