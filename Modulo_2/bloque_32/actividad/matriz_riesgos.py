
"""
BLOQUE 32 - MATRIZ DE RIESGOS
Proyecto: Sistema RAG
"""

# ============================================================
# 1. DEFINICION DE RIESGOS
# ============================================================

RIESGOS = [
    {
        "riesgo": "Inyeccion de prompt mediante documentos indexados",
        "probabilidad": 4,
        "impacto": 4,
        "mitigacion": (
            "Filtro de patrones y descarte de documentos sospechosos "
            "(Bloque 31)"
        ),
    },
    {
        "riesgo": "Exposicion de informacion sensible contenida en documentos recuperados",
        "probabilidad": 3,
        "impacto": 5,
        "mitigacion": (
            "Filtrado del contexto y control de acceso a documentos "
            "(Bloque 31: filtrado; control de acceso pendiente de integrar)"
        ),
    },
    {
        "riesgo": "Respuesta incorrecta por recuperacion de documentos poco relevantes",
        "probabilidad": 3,
        "impacto": 4,
        "mitigacion": (
            "Validacion humana de respuestas de alto impacto "
            "y mejora de recuperacion documental"
        ),
    },
    {
        "riesgo": "Uso de documentos desactualizados como fuente de respuesta",
        "probabilidad": 3,
        "impacto": 3,
        "mitigacion": (
            "Revision de vigencia y versionado del contenido documental"
        ),
    },
    {
        "riesgo": "Falta de disponibilidad del modelo o servicio LLM",
        "probabilidad": 2,
        "impacto": 3,
        "mitigacion": (
            "Registro de errores y trazabilidad de consultas "
            "(Bloque 31)"
        ),
    },
]


# ============================================================
# 2. CLASIFICACION DE RIESGOS
# ============================================================

def calcular_puntaje(probabilidad, impacto):
    """Calcula el puntaje multiplicando probabilidad por impacto."""
    return probabilidad * impacto


def clasificar_riesgo(puntaje):
    """Clasifica el riesgo segun su puntaje."""

    if puntaje >= 15:
        return "CRITICO"
    elif puntaje >= 9:
        return "ALTO"
    elif puntaje >= 4:
        return "MEDIO"
    else:
        return "BAJO"


# ============================================================
# 3. DETECCION DE RIESGOS EN EL LIMITE
# ============================================================

def esta_en_el_limite(probabilidad, impacto):
    """
    Comprueba si modificar en una unidad la probabilidad
    o el impacto cambia la categoria del riesgo.
    """

    puntaje_actual = calcular_puntaje(probabilidad, impacto)
    categoria_actual = clasificar_riesgo(puntaje_actual)

    valores_vecinos = []

    # Variaciones de probabilidad: -1 y +1
    for nueva_probabilidad in (probabilidad - 1, probabilidad + 1):
        if 1 <= nueva_probabilidad <= 5:
            valores_vecinos.append(
                (nueva_probabilidad, impacto)
            )

    # Variaciones de impacto: -1 y +1
    for nuevo_impacto in (impacto - 1, impacto + 1):
        if 1 <= nuevo_impacto <= 5:
            valores_vecinos.append(
                (probabilidad, nuevo_impacto)
            )

    # Comprueba si algun vecino cambia la categoria
    for p_vecina, i_vecino in valores_vecinos:
        puntaje_vecino = calcular_puntaje(p_vecina, i_vecino)
        categoria_vecina = clasificar_riesgo(puntaje_vecino)

        if categoria_vecina != categoria_actual:
            return True

    return False


# ============================================================
# 4. SUPERVISION HUMANA
# ============================================================

SUPERVISION_HUMANA = {

    "Inyeccion de prompt mediante documentos indexados": (
        "Revisar manualmente los documentos marcados por el filtro "
        "antes de reincorporarlos al indice."
    ),

    "Exposicion de informacion sensible contenida en documentos recuperados": (
        "Solicitar autorizacion humana antes de habilitar el acceso "
        "a documentos sensibles."
    ),

    "Respuesta incorrecta por recuperacion de documentos poco relevantes": (
        "Revisar la respuesta y las fuentes antes de entregarla "
        "cuando pueda afectar una decision importante."
    ),

    # CORRECCION: se agrega supervision para este riesgo ALTO.
    "Uso de documentos desactualizados como fuente de respuesta": (
        "Verificar manualmente la fecha y version de los documentos "
        "antes de utilizarlos para generar una respuesta."
    ),
}


# ============================================================
# 5. VALIDACIONES
# ============================================================

def validar_riesgos():
    """Comprueba que los riesgos y sus controles esten completos."""

    assert len(RIESGOS) >= 5, (
        "La matriz debe contener al menos cinco riesgos."
    )

    for riesgo in RIESGOS:

        nombre = riesgo["riesgo"]
        probabilidad = riesgo["probabilidad"]
        impacto = riesgo["impacto"]

        assert 1 <= probabilidad <= 5, (
            f"Probabilidad invalida para: {nombre}"
        )

        assert 1 <= impacto <= 5, (
            f"Impacto invalido para: {nombre}"
        )

        assert riesgo["mitigacion"].strip(), (
            f"Falta mitigacion para: {nombre}"
        )

        puntaje = calcular_puntaje(probabilidad, impacto)
        categoria = clasificar_riesgo(puntaje)

        # Todo riesgo ALTO o CRITICO requiere supervision humana.
        if categoria in ("ALTO", "CRITICO"):
            assert nombre in SUPERVISION_HUMANA, (
                f"Falta supervision humana para: {nombre}"
            )

    # Verifica que existan mitigaciones que referencien
    # bloques implementados del proyecto.
    mitigaciones = [
        riesgo["mitigacion"]
        for riesgo in RIESGOS
    ]

    referencias_bloques = [
        mitigacion
        for mitigacion in mitigaciones
        if "Bloque 31" in mitigacion
    ]

    assert len(referencias_bloques) >= 2, (
        "Se requieren al menos dos mitigaciones "
        "que referencien bloques implementados."
    )

    return True


# ============================================================
# 6. IMPRESION DE LA MATRIZ
# ============================================================

def mostrar_matriz():

    print("\n=== MATRIZ DE RIESGOS ===\n")

    for riesgo in RIESGOS:

        nombre = riesgo["riesgo"]
        probabilidad = riesgo["probabilidad"]
        impacto = riesgo["impacto"]
        mitigacion = riesgo["mitigacion"]

        puntaje = calcular_puntaje(probabilidad, impacto)
        categoria = clasificar_riesgo(puntaje)

        print(f"{categoria:<8} ({puntaje:2}) - {nombre}")
        print(f"Mitigacion: {mitigacion}")

        if esta_en_el_limite(probabilidad, impacto):
            print("AL LIMITE: requiere revision de otra persona")

        print()


# ============================================================
# 7. IMPRESION DE SUPERVISION HUMANA
# ============================================================

def mostrar_supervision():

    print("\n=== SUPERVISION HUMANA ===\n")

    for riesgo in RIESGOS:

        nombre = riesgo["riesgo"]

        puntaje = calcular_puntaje(
            riesgo["probabilidad"],
            riesgo["impacto"]
        )

        categoria = clasificar_riesgo(puntaje)

        if categoria in ("ALTO", "CRITICO"):
            print(f"Riesgo: {nombre}")
            print(f"Accion: {SUPERVISION_HUMANA[nombre]}")
            print()


# ============================================================
# 8. PRUEBAS DE FUNCIONAMIENTO
# ============================================================

def ejecutar_pruebas():

    print("\n=== VALIDACION DE LA MATRIZ ===\n")

    # Prueba de calculo
    assert calcular_puntaje(4, 4) == 16
    assert calcular_puntaje(3, 5) == 15
    assert calcular_puntaje(3, 4) == 12

    print("[OK] Calculo de puntajes")

    # Prueba de clasificacion
    assert clasificar_riesgo(16) == "CRITICO"
    assert clasificar_riesgo(12) == "ALTO"
    assert clasificar_riesgo(6) == "MEDIO"
    assert clasificar_riesgo(2) == "BAJO"

    print("[OK] Clasificacion de riesgos")

    # Prueba de deteccion de limites
    assert esta_en_el_limite(4, 4) is True
    assert esta_en_el_limite(3, 5) is True
    assert esta_en_el_limite(3, 4) is True
    assert esta_en_el_limite(3, 3) is True
    assert esta_en_el_limite(2, 3) is True

    print("[OK] Deteccion de riesgos en el limite")

    # Prueba de supervision humana
    for riesgo in RIESGOS:

        nombre = riesgo["riesgo"]

        puntaje = calcular_puntaje(
            riesgo["probabilidad"],
            riesgo["impacto"]
        )

        categoria = clasificar_riesgo(puntaje)

        if categoria in ("ALTO", "CRITICO"):
            assert nombre in SUPERVISION_HUMANA, (
                f"Falta supervision humana para: {nombre}"
            )

    print("[OK] Supervision humana para riesgos ALTO y CRITICO")

    # Validacion general
    assert validar_riesgos() is True

    print("[OK] Validacion general de la matriz")

    print("\nTODAS LAS PRUEBAS FINALIZARON CORRECTAMENTE")
    print("BLOQUE 32 - MATRIZ DE RIESGOS COMPLETADA")


# ============================================================
# 9. EJECUCION PRINCIPAL
# ============================================================

if __name__ == "__main__":

    mostrar_matriz()
    mostrar_supervision()
    ejecutar_pruebas()
