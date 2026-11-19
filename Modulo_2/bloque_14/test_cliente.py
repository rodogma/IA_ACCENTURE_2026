
# test_cliente.py

import pytest
import cliente

from unittest.mock import Mock, patch


@pytest.fixture(autouse=True)
def reiniciar_costo_total():
    cliente.costo_total_sesion = 0
    yield
    cliente.costo_total_sesion = 0


def test_enviar_peticion_credencial_invalida():
    print("\nProbando credencial inválida...")

    respuesta = Mock(status_code=401)

    with patch.object(cliente, "GEMINI_API_KEY", "clave_simulada"):
        with patch(
            "cliente.requests.post",
            return_value=respuesta
        ):
            with pytest.raises(ValueError):
                cliente.enviar_peticion({"contents": []})

    print("Función enviar_peticion: credencial inválida OK")


def test_enviar_peticion_limite_de_uso():
    print("\nProbando límite de uso...")

    respuesta = Mock(status_code=429)

    with patch.object(cliente, "GEMINI_API_KEY", "clave_simulada"):
        with patch(
            "cliente.requests.post",
            return_value=respuesta
        ):
            with pytest.raises(TimeoutError):
                cliente.enviar_peticion({"contents": []})

    print("Función enviar_peticion: límite de uso OK")


def test_enviar_peticion_exito():
    print("\nProbando petición exitosa...")

    respuesta = Mock(status_code=200)
    respuesta.json.return_value = {"mensaje": "OK"}

    with patch.object(cliente, "GEMINI_API_KEY", "clave_simulada"):
        with patch(
            "cliente.requests.post",
            return_value=respuesta
        ):
            resultado = cliente.enviar_peticion(
                {"contents": []}
            )

    assert resultado == {"mensaje": "OK"}
    print("Respuesta simulada:", resultado)


def test_con_reintento_agota_intentos():
    print("\nProbando reintentos agotados...")

    def siempre_falla():
        raise TimeoutError("Error simulado")

    with patch("cliente.time.sleep") as dormir:
        with pytest.raises(TimeoutError):
            cliente.con_reintento(
                siempre_falla,
                intentos=3
            )

    assert dormir.call_count == 2
    print("Función con_reintento: 3 intentos comprobados")


def test_con_reintento_no_reintenta_value_error():
    print("\nProbando error permanente...")

    funcion = Mock(
        side_effect=ValueError("Error permanente")
    )

    with patch("cliente.time.sleep") as dormir:
        with pytest.raises(ValueError):
            cliente.con_reintento(funcion)

    funcion.assert_called_once()
    dormir.assert_not_called()

    print("Función con_reintento: no repitió error permanente")


def test_registrar_costo_acumula():
    print("\nProbando registro de costo...")

    respuesta = {
        "usageMetadata": {
            "totalTokenCount": 1000
        }
    }

    costo = cliente.registrar_costo(respuesta)

    assert costo == cliente.COSTO_POR_1000_TOKENS
    assert cliente.costo_total_sesion == costo

    print("Costo registrado:", costo)
    print("Costo acumulado:", cliente.costo_total_sesion)


def test_consultar_modelo_convierte_error():
    print("\nProbando conversión de error...")

    with patch(
        "cliente.con_reintento",
        side_effect=TimeoutError("Error simulado")
    ):
        with pytest.raises(RuntimeError):
            cliente.consultar_modelo(
                "¿Cuál es la capital de Chile?"
            )

    print("Función consultar_modelo: error convertido OK")


if __name__ == "__main__":
    raise SystemExit(
        pytest.main([
            __file__,
            "-v",
            "-s"
        ])
    )
