
import re
from cliente import consultar_modelo


def limpiar_texto(texto: str) -> str:
    """Limpia y normaliza el texto."""

    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def tokenizar(texto_limpio: str) -> list[str]:
    """Divide el texto limpio en palabras."""

    return texto_limpio.split()


def procesar_texto(texto: str) -> list[str]:
    """Ejecuta limpieza y tokenización."""

    return tokenizar(limpiar_texto(texto))


def calcular_coincidencia(
    referencia: list[str],
    respuesta: list[str]
) -> float:
    """Calcula coincidencia por palabras."""

    palabras_ref = set(referencia)
    palabras_resp = set(respuesta)

    if not palabras_ref:
        return 0.0

    comunes = palabras_ref & palabras_resp

    return len(comunes) / len(palabras_ref)


def evaluar_respuesta(
    numero: int,
    consulta: str,
    referencia: str
) -> None:

    respuesta = consultar_modelo(consulta)

    # Texto sin procesar
    crudo_ref = referencia.split()
    crudo_resp = respuesta.split()

    pct_crudo = calcular_coincidencia(
        crudo_ref,
        crudo_resp
    )

    # Texto procesado
    tokens_ref = procesar_texto(referencia)
    tokens_resp = procesar_texto(respuesta)

    pct_procesado = calcular_coincidencia(
        tokens_ref,
        tokens_resp
    )

    print("\n" + "=" * 50)
    print(f"CASO {numero}")
    print("=" * 50)

    print("Consulta:", consulta)
    print("Referencia:", referencia)
    print("Respuesta Gemini:", respuesta)

    print("Tokens referencia:", tokens_ref)
    print("Tokens respuesta:", tokens_resp)

    print(f"Coincidencia cruda: {pct_crudo:.1%}")
    print(f"Coincidencia procesada: {pct_procesado:.1%}")


def main():

    casos = [
        (
            "¿Qué es Python? Responde en una oración.",
            "Python es un lenguaje de programación interpretado."
        ),
        (
            "¿Qué es una variable en programación? "
            "Responde en una oración.",
            "Una variable almacena un valor en memoria."
        ),
        (
            "¿Qué es una función en Python? "
            "Responde en una oración.",
            "Una función es un bloque de código reutilizable."
        )
    ]

    for numero, (consulta, referencia) in enumerate(
        casos, start=1
    ):
        try:
            evaluar_respuesta(
                numero,
                consulta,
                referencia
            )

        except Exception as error:
            print(f"Error en el caso {numero}: {error}")


if __name__ == "__main__":
    main()
