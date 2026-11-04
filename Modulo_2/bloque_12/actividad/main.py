
from cliente import consultar_modelo


try:
    respuesta = consultar_modelo(
        "¿Cuál es la capital de Chile?"
    )

    print("Respuesta:", respuesta)

except ValueError as error:
    print(f"Error de configuración: {error}")

except RuntimeError as error:
    print(f"Error del servicio: {error}")
