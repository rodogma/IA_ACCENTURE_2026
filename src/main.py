
import requests
from Consumir_api import obtener_dato_de_prueba


def main():

    print("=" * 50)
    print("       MINIAPLICACIÓN GOOGLE GEMINI")
    print("=" * 50)
    print("Escribe tus preguntas.")
    print("Para terminar, escribe 'salir'.")

    while True:

        # Aquí escribes tu pregunta
        pregunta = input("\ncual es tu pregunta: ")

        # Finalizar programa
        if pregunta.strip().lower() == "salir":
            print("\nPrograma finalizado.")
            break

        try:
            # Consultar Gemini
            respuesta = obtener_dato_de_prueba(pregunta)

            # Mostrar resultado
            print("\nRespuesta de Gemini:")
            print(respuesta)

        except requests.exceptions.Timeout:
            print(
                "Error: Gemini tardó demasiado en responder."
            )

        except requests.exceptions.HTTPError as error:
            print(
                f"Error HTTP: {error.response.status_code}"
            )
            print("Detalle:", error.response.text)

        except requests.exceptions.ConnectionError:
            print(
                "Error: no se pudo conectar con Gemini."
            )

        except requests.exceptions.RequestException as error:
            print(
                f"Error en la petición: {error}"
            )

        except TypeError as error:
            print(
                f"Error de tipo de dato: {error}"
            )

        except ValueError as error:
            print(
                f"Error de validación: {error}"
            )

        except (KeyError, IndexError) as error:
            print(
                f"Error al procesar el JSON: {error}"
            )

        except (EOFError, KeyboardInterrupt):
            print("\nPrograma interrumpido.")
            break


if __name__ == "__main__":
    main()
