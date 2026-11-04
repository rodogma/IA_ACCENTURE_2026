
from unittest.mock import patch
import cliente
from cliente import consultar_modelo


def probar_credencial():
    print("\nPRUEBA: Credencial inválida")
    contador = {"n": 0}

    def simular_error(url, cuerpo):
        contador["n"] += 1
        raise ValueError(
            "Credencial inválida o sin permiso. "
            "Revisa tu GEMINI_API_KEY."
        )

    with patch.object(
        cliente, "enviar_peticion",
        side_effect=simular_error
    ):
        try:
            consultar_modelo("Hola")
        except ValueError as error:
            print(error)
            assert contador["n"] == 1
            print("CORRECTO: no hubo reintentos.")
        else:
            raise AssertionError("Se esperaba ValueError")


def probar_reintentos():
    print("\nPRUEBA: Límite de uso")
    contador = {"n": 0}

    def simular_envio(url, cuerpo):
        contador["n"] += 1

        if contador["n"] < 3:
            raise TimeoutError("HTTP 429")

        return {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Santiago"}]
                }
            }]
        }

    with patch.object(
        cliente, "enviar_peticion",
        side_effect=simular_envio
    ):
        resultado = consultar_modelo("Capital de Chile")

    assert resultado == "Santiago"
    assert contador["n"] == 3
    print("Respuesta:", resultado)
    print("CORRECTO: funcionó en el tercer intento.")


def probar_agotamiento():
    print("\nPRUEBA: Reintentos agotados")
    contador = {"n": 0}

    def simular_error(url, cuerpo):
        contador["n"] += 1
        raise TimeoutError("HTTP 429")

    with patch.object(
        cliente, "enviar_peticion",
        side_effect=simular_error
    ):
        try:
            consultar_modelo("Hola")
        except RuntimeError as error:
            print(error)
            assert contador["n"] == 3
            print("CORRECTO: RuntimeError tras tres intentos.")
        else:
            raise AssertionError("Se esperaba RuntimeError")


if __name__ == "__main__":
    probar_credencial()
    probar_reintentos()
    probar_agotamiento()
