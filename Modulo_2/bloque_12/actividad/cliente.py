
from cliente_api import (
    armar_peticion,
    enviar_peticion,
    extraer_texto
)

from cliente_reintento import con_reintento


def consultar_modelo(
    pregunta: str,
    system_instruction: str = ""
) -> str:

    # Preparar la petición
    url, cuerpo = armar_peticion(
        pregunta,
        system_instruction
    )

    # Enviar con reintentos automáticos
    try:
        respuesta = con_reintento(
            lambda: enviar_peticion(url, cuerpo)
        )

    # Error cuando se agotan los intentos
    except TimeoutError as error:
        raise RuntimeError(
            "El servicio no respondió tras varios intentos. "
            "Intenta más tarde."
        ) from error

    # Extraer y devolver el texto
    return extraer_texto(respuesta)
