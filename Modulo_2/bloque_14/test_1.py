
# test_1.py

import pytest

from cliente_api import (
    armar_peticion,
    extraer_texto
)


def test_suma():
    print("\nProbando suma...")
    assert 2 + 2 == 4
    print("Resultado: 4")


def test_armar_peticion_correctamente():
    print("\nEjecutando armar_peticion...")

    resultado = armar_peticion("Hola Gemini")

    assert (
        resultado["contents"][0]["parts"][0]["text"]
        == "Hola Gemini"
    )

    print("Petición generada:", resultado)


def test_armar_peticion_vacia():
    print("\nProbando pregunta vacía...")

    with pytest.raises(ValueError):
        armar_peticion("")

    print("Validación de pregunta vacía: OK")


def test_extraer_texto_correctamente():
    print("\nEjecutando extraer_texto...")

    respuesta = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "Santiago"}
                    ]
                }
            }
        ]
    }

    resultado = extraer_texto(respuesta)

    assert resultado == "Santiago"
    print("Texto extraído:", resultado)


def test_extraer_texto_sin_candidatos():
    print("\nProbando respuesta sin candidatos...")

    with pytest.raises(ValueError):
        extraer_texto({"candidates": []})

    print("Validación sin candidatos: OK")


if __name__ == "__main__":
    raise SystemExit(
        pytest.main([
            __file__,
            "-v",
            "-s"
        ])
    )
