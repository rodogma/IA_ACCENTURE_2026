
from pipeline_texto import (
    limpiar_texto,
    tokenizar,
    procesar_texto,
    calcular_coincidencia
)


def test_normaliza_mayusculas_y_puntuacion():
    resultado = procesar_texto("El Cielo, es AZUL!")
    assert resultado == ["el", "cielo", "es", "azul"]


def test_solo_puntuacion():
    resultado = procesar_texto("¡¡¡...!!!")
    assert resultado == []


def test_texto_vacio():
    assert procesar_texto("") == []


def test_limpiar_texto():
    assert limpiar_texto("HOLA, Mundo!") == "hola mundo"


def test_tokenizar():
    assert tokenizar("hola mundo") == ["hola", "mundo"]


def test_coincidencia_perfecta():
    referencia = ["python", "es", "útil"]
    respuesta = ["python", "es", "útil"]

    assert calcular_coincidencia(
        referencia, respuesta
    ) == 1.0


def test_referencia_vacia():
    assert calcular_coincidencia([], ["hola"]) == 0.0
if __name__ == "__main__":
    import pytest
    import sys

    print("\nINICIANDO PRUEBAS DEL BLOQUE 15\n")

    resultado = pytest.main([
        __file__,
        "-v"
    ])

    sys.exit(resultado)