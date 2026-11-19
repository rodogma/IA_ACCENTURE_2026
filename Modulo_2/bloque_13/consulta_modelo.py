
from consumir_gemini import (
    armar_peticion,
    calcular_costo_peticion,
    extraer_texto,
    enviar_peticion
)

from reintento import con_reintento


PRECIO_ENTRADA = 0.0001
PRECIO_SALIDA = 0.0025

costo_total_sesion = 0.0


response_schema = {
    "type": "OBJECT",
    "properties": {
        "rta": {"type": "STRING"},
        "fuente": {"type": "STRING"}
    },
    "required": ["rta", "fuente"]
}


def consultar_modelo(
    pregunta: str,
    system_instruction: str = "",
    respuesta_json: bool = False
) -> str:

    global costo_total_sesion

    esquema = (
        response_schema if respuesta_json else None
    )

    url, body = armar_peticion(
        pregunta,
        system_instruction,
        esquema
    )

    try:
        respuesta = con_reintento(
            lambda: enviar_peticion(url, body),
            intentos=5,
            espera_base=5,
            espera_maxima=10
        )

    except TimeoutError as error:
        raise RuntimeError(
            "El servicio no respondió tras varios intentos. "
            "Intenta más tarde."
        ) from error

    try:
        costo = calcular_costo_peticion(
            respuesta,
            PRECIO_ENTRADA,
            PRECIO_SALIDA
        )

        costo_total_sesion += costo

        print(f"Costo de la petición: ${costo:.6f}")

        print(
            f"Costo acumulado de sesión: "
            f"${costo_total_sesion:.6f}"
        )

    except ValueError as error:
        print(
            f"No se pudo calcular el costo: {error}"
        )

    texto = extraer_texto(respuesta)

    if respuesta_json:
        from consumir_gemini import parsear_respuesta_json
        parsear_respuesta_json(texto)

    return texto


if __name__ == "__main__":

    print("PRUEBA LOCAL DE GEMINI")

    for i in range(1):

        print(f"\nIteración {i + 1}:")

        try:
            resultado = consultar_modelo(
                "¿Quién ganó la carrera de Austin 2024?",
                "Indica escudería, piloto y "
                "posiciones finales en lista."
            )

            print("\nRespuesta:")
            print(resultado)

        except (ValueError, RuntimeError) as error:
            print(f"ERROR: {error}")
