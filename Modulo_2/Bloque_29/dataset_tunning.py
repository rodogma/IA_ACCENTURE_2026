
import json
from collections import Counter
from google.genai import types


# ==================================================
# PASO 1: CREAR DATASET DE TUNING
# Proyecto: Asistente de redacción profesional
# ==================================================

# El objetivo es transformar mensajes informales
# en textos profesionales con formato JSON.

ejemplos_raw = [
    (
        "Necesito que me mandes el informe hoy.",
        {
            "categoria": "solicitud",
            "respuesta": "Agradecería que pudiera remitir el informe durante el día de hoy."
        }
    ),
    (
        "Mándame los documentos que faltan.",
        {
            "categoria": "solicitud",
            "respuesta": "Solicito amablemente el envío de la documentación pendiente."
        }
    ),
    (
        "Quiero que revises este archivo.",
        {
            "categoria": "solicitud",
            "respuesta": "Agradecería que pudiera revisar el archivo adjunto."
        }
    ),
    (
        "Hay un problema con el sistema.",
        {
            "categoria": "incidencia",
            "respuesta": "Se ha identificado una incidencia en el sistema que requiere revisión."
        }
    ),
    (
        "La aplicación no funciona bien.",
        {
            "categoria": "incidencia",
            "respuesta": "Se han detectado dificultades en el funcionamiento de la aplicación."
        }
    ),
    (
        "No puedo entrar a mi cuenta.",
        {
            "categoria": "incidencia",
            "respuesta": "Se presenta un inconveniente que impide el acceso a la cuenta."
        }
    ),
    (
        "La reunión será mañana.",
        {
            "categoria": "informacion",
            "respuesta": "Se informa que la reunión se llevará a cabo el día de mañana."
        }
    ),
    (
        "Ya envié los documentos.",
        {
            "categoria": "informacion",
            "respuesta": "Se comunica que la documentación correspondiente ha sido enviada."
        }
    ),
    (
        "El informe está listo.",
        {
            "categoria": "informacion",
            "respuesta": "Se informa que el informe se encuentra finalizado y disponible para su revisión."
        }
    ),
    (
        "Todavía estoy esperando tu respuesta.",
        {
            "categoria": "seguimiento",
            "respuesta": "Quedo atento a su respuesta respecto de la solicitud previamente realizada."
        }
    ),
    (
        "¿Qué pasó con el documento?",
        {
            "categoria": "seguimiento",
            "respuesta": "Agradecería conocer el estado actual de la documentación solicitada."
        }
    ),
    (
        "Avísame cuando termines.",
        {
            "categoria": "seguimiento",
            "respuesta": "Agradecería que me informara una vez finalizada la actividad."
        }
    )
]


# Convertir los ejemplos al formato requerido
# por la biblioteca google-genai.

examples = [
    types.TuningExample(
        text_input=texto,
        output=json.dumps(
            salida,
            ensure_ascii=False
        )
    )
    for texto, salida in ejemplos_raw
]

print("====================================")
print("PASO 1: DATASET CREADO")
print("====================================")

print(f"{len(examples)} ejemplos construidos")
print("Primer ejemplo:")
print(examples[0])


# ==================================================
# PASO 2: REVISAR BALANCE DE CATEGORÍAS
# ==================================================

def chequear_balance(
    ejemplos_raw: list[tuple[str, dict]],
    clave: str
) -> Counter:

    categorias = Counter(
        salida[clave]
        for _, salida in ejemplos_raw
    )

    return categorias


balance = chequear_balance(
    ejemplos_raw,
    "categoria"
)

print("\n====================================")
print("PASO 2: BALANCE DEL DATASET")
print("====================================")

for categoria, cantidad in balance.most_common():
    print(f"{categoria}: {cantidad}")


# ==================================================
# PASO 3: VALIDAR DATASET
# ==================================================

def validar_dataset(
    examples: list[types.TuningExample],
    claves_esperadas: tuple[str, ...]
) -> list[str]:

    problemas = []
    vistos = set()

    for i, ejemplo in enumerate(examples):

        # Verificar entrada vacía
        if (
            not ejemplo.text_input
            or not ejemplo.text_input.strip()
        ):
            problemas.append(
                f"Ejemplo {i}: text_input vacío"
            )

        # Verificar salida vacía
        if (
            not ejemplo.output
            or not ejemplo.output.strip()
        ):
            problemas.append(
                f"Ejemplo {i}: output vacío"
            )
            continue

        # Detectar entradas duplicadas
        if ejemplo.text_input in vistos:
            problemas.append(
                f"Ejemplo {i}: text_input duplicado"
            )

        vistos.add(ejemplo.text_input)

        # Verificar JSON válido
        try:
            salida = json.loads(ejemplo.output)

        except json.JSONDecodeError:
            problemas.append(
                f"Ejemplo {i}: JSON inválido"
            )
            continue

        # Comprobar estructura de objeto
        if not isinstance(salida, dict):
            problemas.append(
                f"Ejemplo {i}: output no es un objeto JSON"
            )
            continue

        # Verificar claves obligatorias
        for clave in claves_esperadas:

            if clave not in salida:
                problemas.append(
                    f"Ejemplo {i}: falta la clave '{clave}'"
                )

    return problemas


problemas = validar_dataset(
    examples,
    claves_esperadas=(
        "categoria",
        "respuesta"
    )
)

print("\n====================================")
print("PASO 3: VALIDACIÓN DEL DATASET")
print("====================================")

print(
    f"{len(examples)} ejemplos, "
    f"{len(problemas)} problemas encontrados"
)

for problema in problemas:
    print("-", problema)


# ==================================================
# PASO 4: COMPROBAR QUE EL VALIDADOR
# DETECTA ERRORES
# ==================================================

print("\n====================================")
print("PASO 4: PRUEBAS DEL VALIDADOR")
print("====================================")

# Prueba 1: entrada duplicada

ejemplo_duplicado = types.TuningExample(
    text_input=examples[0].text_input,
    output=examples[0].output
)

dataset_duplicado = examples + [
    ejemplo_duplicado
]

errores_duplicado = validar_dataset(
    dataset_duplicado,
    ("categoria", "respuesta")
)

print("Prueba de duplicados:")
print(errores_duplicado)

assert any(
    "duplicado" in error
    for error in errores_duplicado
)


# Prueba 2: falta una clave obligatoria

ejemplo_incompleto = types.TuningExample(
    text_input="Necesito una respuesta urgente.",
    output=json.dumps({
        "categoria": "solicitud"
    })
)

errores_clave = validar_dataset(
    [ejemplo_incompleto],
    ("categoria", "respuesta")
)

print("\nPrueba de clave faltante:")
print(errores_clave)

assert any(
    "respuesta" in error
    for error in errores_clave
)


# ==================================================
# RESULTADO FINAL
# ==================================================

print("\n====================================")
print("RESULTADO FINAL DEL LABORATORIO")
print("====================================")

if len(examples) >= 10 and not problemas:

    print("DATASET VALIDADO CORRECTAMENTE")
    print("Cantidad de ejemplos:", len(examples))
    print("Categorías:", len(balance))
    print("Problemas encontrados:", len(problemas))
    print("Pruebas de errores: SUPERADAS")
    print("Dataset listo para preparar el tuning.")

else:

    print("El dataset requiere correcciones.")

# MOSTRAR LOS 12 EJEMPLOS DEL DATASET

print("\n========== MIS 12 EJEMPLOS ==========")

for numero, (texto, salida) in enumerate(ejemplos_raw, start=1):
    print(f"\nEJEMPLO {numero}")
    print(f"Texto original: {texto}")
    print(f"Categoría: {salida['categoria']}")
    print(f"Respuesta profesional: {salida['respuesta']}")
    print("-" * 50)
