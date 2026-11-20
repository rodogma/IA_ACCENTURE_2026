
import consulta_modelo

from consulta_modelo import consultar_modelo


if __name__ == "__main__":

    print("PRUEBA DE CONEXIÓN CON GEMINI")

    try:
        respuesta = consultar_modelo(
            "¿Cuál es la capital de Chile?"
        )

        print("\nRespuesta del modelo:")
        print(respuesta)

        print(
            "\nCosto acumulado de la sesión: "
            f"${consulta_modelo.costo_total_sesion:.6f}"
        )

    except (ValueError, RuntimeError) as error:

        print("\nERROR:")
        print(error)
