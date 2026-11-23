
# ============================================================
# BLOQUE 30 - ESTIMACION DEL COSTO COMPUTACIONAL
# Fine-tuning de modelos de IA
#
# Este programa NO ejecuta entrenamientos.
# NO consulta la API de Gemini.
# NO genera cargos.
# ============================================================


def calcular_costo_computacional(
    numero_ejemplos,
    tokens_por_ejemplo,
    epocas,
    precio_por_millon_tokens
):
    # Tokens del conjunto de entrenamiento
    tokens_dataset = numero_ejemplos * tokens_por_ejemplo

    # Tokens procesados durante todas las epocas
    tokens_entrenamiento = tokens_dataset * epocas

    # Estimacion monetaria
    costo_estimado = (
        tokens_entrenamiento / 1_000_000
    ) * precio_por_millon_tokens

    return {
        "ejemplos_usados": numero_ejemplos,
        "tokens_dataset": tokens_dataset,
        "epocas": epocas,
        "tokens_entrenamiento": tokens_entrenamiento,
        "costo_estimado": costo_estimado
    }


# ============================================================
# DATOS DE EJEMPLO
# Sustituir por datos reales cuando esten disponibles
# ============================================================

numero_ejemplos = 200
tokens_por_ejemplo = 500
epocas = 3

# Precio HIPOTETICO en USD por millon de tokens.
# NO es una tarifa oficial de Google.
precio_por_millon_tokens = 5.00


# ============================================================
# CALCULO
# ============================================================

resultado = calcular_costo_computacional(
    numero_ejemplos,
    tokens_por_ejemplo,
    epocas,
    precio_por_millon_tokens
)


# ============================================================
# RESULTADOS
# ============================================================

print("=" * 55)
print("BLOQUE 30 - ESTIMACION DE COSTO COMPUTACIONAL")
print("=" * 55)

print("Ejemplos usados:", resultado["ejemplos_usados"])
print("Tokens del dataset:", resultado["tokens_dataset"])
print("Epocas:", resultado["epocas"])

print(
    "Tokens procesados durante entrenamiento:",
    resultado["tokens_entrenamiento"]
)

print(
    f"Costo hipotetico: "
    f"USD {resultado['costo_estimado']:.2f}"
)

print("=" * 55)
print("NOTA: Estimacion educativa, no facturacion real.")
print("No se ejecuto ningun trabajo de tuning.")
