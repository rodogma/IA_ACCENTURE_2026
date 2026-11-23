
from unittest.mock import MagicMock

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_paso_clasificacion,
    construir_cadena_queja_segura,
    procesar_mensaje_seguro,
)


# ==========================================
# TEST 1: ENRUTAMIENTO A QUEJA
# ==========================================

def test_enrutamiento_va_a_cadena_queja():

    clasificacion_falsa = MagicMock(
        return_value="queja"
    )

    cadena_queja_falsa = MagicMock(
        return_value="respuesta de queja"
    )

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_queja=cadena_queja_falsa,
    )

    resultado = cadena.invoke({
        "mensaje": "esto no funciona"
    })

    assert cadena_queja_falsa.called
    assert resultado == "respuesta de queja"


# ==========================================
# TEST 2: ENRUTAMIENTO A PREGUNTA
# ==========================================

def test_enrutamiento_va_a_cadena_pregunta():

    clasificacion_falsa = MagicMock(
        return_value="pregunta"
    )

    cadena_pregunta_falsa = MagicMock(
        return_value="respuesta de pregunta"
    )

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_pregunta=cadena_pregunta_falsa,
    )

    resultado = cadena.invoke({
        "mensaje": "¿Cómo cambio mi contraseña?"
    })

    assert cadena_pregunta_falsa.called
    assert resultado == "respuesta de pregunta"


# ==========================================
# TEST 3: ENRUTAMIENTO A SUGERENCIA
# ==========================================

def test_enrutamiento_va_a_cadena_sugerencia():

    clasificacion_falsa = MagicMock(
        return_value="sugerencia"
    )

    cadena_sugerencia_falsa = MagicMock(
        return_value="respuesta de sugerencia"
    )

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_sugerencia=cadena_sugerencia_falsa,
    )

    resultado = cadena.invoke({
        "mensaje": "Podrían aumentar la fuente"
    })

    assert cadena_sugerencia_falsa.called
    assert resultado == "respuesta de sugerencia"


# ==========================================
# TEST 4: RUTA POR DEFECTO
# ==========================================

def test_enrutamiento_va_a_cadena_default():

    clasificacion_falsa = MagicMock(
        return_value="desconocido"
    )

    cadena_default_falsa = MagicMock(
        return_value="respuesta por defecto"
    )

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_pregunta=cadena_default_falsa,
    )

    resultado = cadena.invoke({
        "mensaje": "Mensaje desconocido"
    })

    assert cadena_default_falsa.called
    assert resultado == "respuesta por defecto"


# ==========================================
# TEST 5: NORMALIZACION
# ==========================================

def test_clasificacion_normaliza_antes_de_comparar():

    modelo_falso = MagicMock(
        return_value=AIMessage(content=" Queja \n")
    )

    cadena = construir_paso_clasificacion(
        modelo_falso
    )

    resultado = cadena.invoke({
        "mensaje": "algo salió mal"
    })

    assert resultado == "queja"


# ==========================================
# TEST 6: FALLBACK ANTE ERROR EN QUEJA
# ==========================================

def test_cadena_queja_usa_fallback_ante_fallo_del_modelo():

    def fallar_a_proposito(datos):
        raise ConnectionError("simulado")

    cadena_queja_falsa = RunnableLambda(
        fallar_a_proposito
    )

    cadena_queja_segura = (
        construir_cadena_queja_segura(
            cadena_queja_falsa
        )
    )

    resultado = cadena_queja_segura.invoke({
        "mensaje": "esto no funciona"
    })

    assert "equipo" in resultado.lower()


# ==========================================
# TEST 7: FALLO EN CLASIFICACION
# ==========================================

def test_procesar_mensaje_seguro_no_propaga_excepciones():

    clasificacion_falsa = MagicMock()

    clasificacion_falsa.side_effect = ConnectionError(
        "simulado"
    )

    cadena_falsa = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
    )

    resultado = procesar_mensaje_seguro(
        cadena_falsa,
        "mensaje de prueba"
    )

    assert "no pudimos procesar" in resultado.lower()
