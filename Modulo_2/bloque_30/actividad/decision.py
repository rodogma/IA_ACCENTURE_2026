
from pathlib import Path


# ============================================================
# BLOQUE 31 - DECISION DE PERSONALIZACION
# Proyecto: Asistente RAG para maquinaria de construccion
# ============================================================


# PASO 1: METODO DE DECISION

def recomendar_estrategia(respuestas):
    puntos = {
        "RAG": 0,
        "Fine-tuning completo": 0,
        "PEFT": 0
    }

    if respuestas["informacion_cambia_seguido"]:
        puntos["RAG"] += 3

    if respuestas["problema_de_formato_o_tono"]:
        puntos["PEFT"] += 2
        puntos["Fine-tuning completo"] += 1

    if respuestas["dataset_grande_y_de_calidad"]:
        puntos["Fine-tuning completo"] += 2
        puntos["PEFT"] += 1

    if respuestas["presupuesto_limitado_o_iterar_rapido"]:
        puntos["RAG"] += 2
        puntos["PEFT"] += 1

    if respuestas["necesita_multiples_variantes"]:
        puntos["PEFT"] += 2

    maximo = max(puntos.values())

    ganadoras = [
        tecnica
        for tecnica, puntuacion in puntos.items()
        if puntuacion == maximo
    ]

    return puntos, ganadoras


# ============================================================
# RESPUESTAS DEL PROYECTO
# ============================================================
# IMPORTANTE:
# Son respuestas iniciales para el proyecto RAG.
# Comprueba los criterios antes de entregar la actividad.
#
# informacion_cambia_seguido:
# True solo si verificas cambios al menos mensuales.
#
# problema_de_formato_o_tono:
# True si al menos 3 de 20 respuestas incumplen el formato.
#
# dataset_grande_y_de_calidad:
# True si tienes al menos 200 ejemplos etiquetados
# y una muestra de 20 sin contradicciones.
#
# presupuesto_limitado_o_iterar_rapido:
# True si puedes costear como maximo 2 entrenamientos
# o necesitas resultados en menos de un dia.
#
# necesita_multiples_variantes:
# True si necesitas al menos 2 versiones del modelo.


respuestas_mi_caso = {
    "informacion_cambia_seguido": False,
    "problema_de_formato_o_tono": False,
    "dataset_grande_y_de_calidad": False,
    "presupuesto_limitado_o_iterar_rapido": True,
    "necesita_multiples_variantes": False
}


# Evidencias disponibles y comprobaciones pendientes
evidencias = {
    "informacion_cambia_seguido":
        "Pendiente: revisar fechas de modificacion de las "
        "fuentes durante los ultimos 3 meses.",

    "problema_de_formato_o_tono":
        "Pendiente: revisar 20 respuestas y contar cuantos "
        "incumplimientos de formato o tono existen.",

    "dataset_grande_y_de_calidad":
        "El proyecto tiene 9 casos de evaluacion de "
        "recuperacion, pero no consta un dataset de "
        "200 ejemplos etiquetados para entrenamiento.",

    "presupuesto_limitado_o_iterar_rapido":
        "Supuesto por confirmar: se prioriza iterar "
        "rapidamente sin financiar multiples entrenamientos.",

    "necesita_multiples_variantes":
        "Actualmente se trabaja con un unico asistente RAG; "
        "no se ha definido una necesidad de varias versiones."
}


# Validacion
if any(
    valor is None
    for valor in respuestas_mi_caso.values()
):
    raise SystemExit(
        "Completa las cinco respuestas con True o False."
    )


puntos, ganadoras = recomendar_estrategia(
    respuestas_mi_caso
)

print("=" * 60)
print("RESULTADO DEL METODO DE DECISION")
print("=" * 60)

for tecnica, puntuacion in sorted(
    puntos.items(),
    key=lambda elemento: -elemento[1]
):
    print(f"{tecnica}: {puntuacion} puntos")

print("\nTecnica(s) candidata(s):")
print(", ".join(ganadoras))


# ============================================================
# PASO 2: GENERAR DOCUMENTO MARKDOWN
# ============================================================

def generar_esqueleto_decision(problema, puntos, ganadoras):
    empate = len(ganadoras) > 1
    lineas = []

    lineas.append("# Decision de personalizacion")
    lineas.append("")

    # SECCION 1
    lineas.append("## 1. El problema")
    lineas.append(problema)
    lineas.append("")

    lineas.append("### Evidencia y criterios")
    lineas.append("")

    for clave, valor in respuestas_mi_caso.items():
        lineas.append(
            f"- **{clave}: {valor}**. {evidencias[clave]}"
        )

    lineas.append("")

    # SECCION 2
    lineas.append("## 2. Resultado del metodo de decision")
    lineas.append("")

    for tecnica, puntuacion in sorted(
        puntos.items(),
        key=lambda elemento: -elemento[1]
    ):
        lineas.append(
            f"- {tecnica}: {puntuacion} puntos"
        )

    lineas.append("")

    if empate:
        lineas.append(
            f"**Empate entre: {', '.join(ganadoras)}**"
        )
    else:
        lineas.append(
            f"**Tecnica mejor puntuada: {ganadoras[0]}**"
        )

    lineas.append("")

    # SECCION 3
    lineas.append("## 3. Tecnica elegida y por que")
    lineas.append("")

    if empate:
        lineas.append(
            "[COMPLETAR: resolver el empate considerando "
            "datos, computo y tiempo.]"
        )
    elif ganadoras[0] == "RAG":
        lineas.append(
            "Se propone RAG porque el proyecto ya dispone "
            "de un sistema de recuperacion semantica basado "
            "en embeddings y Chroma. Esta estrategia permite "
            "incorporar documentos al corpus sin entrenar "
            "nuevamente los parametros del modelo."
        )
    elif ganadoras[0] == "PEFT":
        lineas.append(
            "Se propone PEFT porque permite adaptar "
            "el comportamiento del modelo entrenando "
            "una cantidad reducida de parametros."
        )
    else:
        lineas.append(
            "Se propone Fine-tuning completo cuando "
            "existen suficientes datos etiquetados, "
            "recursos de computo y necesidad de modificar "
            "el comportamiento general del modelo."
        )

    lineas.append("")

    # SECCION 4
    lineas.append("## 4. Que necesitarias para ejecutarla")
    lineas.append("")

    if ganadoras == ["RAG"]:
        lineas.append(
            "El proyecto ya cuenta con 5 documentos "
            "indexados en Chroma y 9 casos de evaluacion "
            "de recuperacion. Para ampliar el sistema "
            "se deben identificar nuevas fuentes de "
            "maquinaria, cimentacion y procedimientos "
            "tecnicos, verificar su calidad y agregarlas "
            "al indice vectorial."
        )
        lineas.append("")
        lineas.append(
            "**Pendiente:** definir y contar exactamente "
            "cuantos documentos adicionales se necesitan "
            "antes de entregar la actividad."
        )
    else:
        lineas.append(
            "[COMPLETAR: indicar el numero actual de "
            "ejemplos etiquetados, la cantidad objetivo "
            "y cuantos faltan.]"
        )

    lineas.append("")
    lineas.append(
        "**Nota:** verificar las respuestas y evidencias "
        "antes de considerar definitiva esta decision."
    )

    return "\n".join(lineas)


problema = (
    "El asistente de maquinaria de construccion necesita "
    "responder preguntas tecnicas utilizando informacion "
    "documental verificable y mantener sus respuestas "
    "alineadas con las fuentes disponibles."
)

documento = generar_esqueleto_decision(
    problema,
    puntos,
    ganadoras
)


# Guardar el documento junto a decision.py
ruta_salida = (
    Path(__file__).resolve().parent
    / "decision_personalizacion.md"
)

ruta_salida.write_text(
    documento,
    encoding="utf-8"
)

print("\n" + "=" * 60)
print("DOCUMENTO GENERADO")
print("=" * 60)
print(f"Archivo: {ruta_salida}")
print("\nContenido:\n")
print(documento)
