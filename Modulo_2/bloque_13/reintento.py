
import time
import random

from typing import Callable, Any


def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_base: float = 2,
    espera_maxima: float = 30,
) -> Any:

    if intentos < 1:
        raise ValueError(
            "La cantidad de intentos debe ser mayor que cero."
        )

    if espera_base < 0 or espera_maxima < 0:
        raise ValueError(
            "Los tiempos de espera no pueden ser negativos."
        )

    for intento in range(1, intentos + 1):

        try:
            print(
                f"Ejecutando intento {intento} de {intentos}"
            )

            resultado = funcion()

            print(
                f"Petición exitosa en el intento {intento}."
            )

            return resultado

        except TimeoutError as error:

            if intento == intentos:
                print("Se agotaron todos los reintentos.")

                raise TimeoutError(
                    f"El servicio falló tras {intentos} intentos."
                ) from error

            espera = min(
                espera_base * (2 ** (intento - 1)),
                espera_maxima
            )

            espera_con_jitter = espera + random.uniform(
                0,
                espera * 0.1
            )

            print(
                f"Intento {intento} falló: {error}"
            )

            print(
                f"Reintentando en "
                f"{espera_con_jitter:.1f} segundos..."
            )

            time.sleep(espera_con_jitter)



if __name__ == "__main__":

    from consumir_gemini import (
        armar_peticion,
        enviar_peticion,
        extraer_texto,
        calcular_costo_peticion
    )

    print("PRUEBA DE REINTENTOS CON GEMINI")

    contador = 0

    # Preparar petición real
    url, body = armar_peticion(
        "¿Cuál es la capital de Chile?",
        "Responde brevemente."
    )

    def prueba_reintentos():
        global contador

        contador += 1

        # Simular errores en los primeros dos intentos
        if contador < 3:
            raise TimeoutError(
                "Simulación de error temporal."
            )

        # Tercer intento: consultar realmente a Gemini
        return enviar_peticion(url, body)

    try:
        respuesta = con_reintento(
            prueba_reintentos,
            intentos=5,
            espera_base=2,
            espera_maxima=10
        )

        # Mostrar respuesta y tokens
        texto = extraer_texto(respuesta)

        # Calcular costos con las tarifas de tu ejercicio
        costo = calcular_costo_peticion(
            respuesta,
            0.0001,
            0.0025
        )

        print("\n========== COSTOS ==========")
        print(f"Costo de la petición: ${costo:.6f}")
        print(f"Costo acumulado: ${costo:.6f}")

        print("\n========== RESPUESTA ==========")
        print(texto)

    except (TimeoutError, ValueError, RuntimeError) as error:
        print(f"\nERROR: {error}")
