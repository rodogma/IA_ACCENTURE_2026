
import pytest
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage

from cadena_tres_pasos import construir_cadena


# ==========================================
# TEST: CADENA DE TRES PASOS
# ==========================================

def test_cadena_conecta_los_tres_pasos():

    print("\n" + "=" * 50)
    print("INICIANDO TEST DE LANGCHAIN")
    print("=" * 50)

    # PASO 1: CREAR MODELO FALSO
    modelo_falso = MagicMock()

    # PASO 2: SIMULAR RESPUESTAS DE GEMINI
    modelo_falso.side_effect = [
        AIMessage(
            content="Categoría: Acceso\nPrioridad: Alta"
        ),
        AIMessage(
            content="Contacte al equipo de soporte TI."
        ),
        AIMessage(
            content=(
                "## Respuesta final\n"
                "Contacte al equipo de soporte TI "
                "para revisar el bloqueo de su cuenta."
            )
        ),
    ]

    # PASO 3: CONSTRUIR CADENA
    cadena = construir_cadena(modelo_falso)

    # PASO 4: EJECUTAR CADENA
    resultado = cadena.invoke({
        "texto": "Mi correo corporativo está bloqueado."
    })

    # MOSTRAR RESULTADOS
    print("\nRESULTADO DEL TEST:")
    print("-" * 50)
    print(resultado)
    print("-" * 50)

    print(
        "\nCantidad de llamadas:",
        modelo_falso.call_count
    )

    print("Tipo de resultado:", type(resultado))

    # PASO 5: VALIDACIONES
    assert modelo_falso.call_count == 3, (
        "ERROR: La cadena no ejecutó los 3 pasos"
    )

    assert isinstance(resultado, str), (
        "ERROR: El resultado no es un string"
    )

    assert "soporte TI" in resultado, (
        "ERROR: No se encontró el texto esperado"
    )

    print("\nTEST SUPERADO CORRECTAMENTE")
    print("=" * 50)


# ==========================================
# EJECUTAR PYTEST DESDE VS CODE
# ==========================================

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "-s"
    ])

