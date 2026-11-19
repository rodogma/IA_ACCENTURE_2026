
import json
import sys
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parent
MODULO_DIR = BASE_DIR.parent

sys.path.insert(
    0, str(MODULO_DIR / "bloque_15")
)

from cliente import consultar_modelo
from pipeline_texto import procesar_texto


def calcular_metricas(referencia: str, respuesta: str) -> dict:
    ref = Counter(procesar_texto(referencia))
    resp = Counter(procesar_texto(respuesta))

    comunes = sum((ref & resp).values())
    total_ref = sum(ref.values())
    total_resp = sum(resp.values())

    precision = comunes / total_resp if total_resp else 0.0
    cobertura = comunes / total_ref if total_ref else 0.0

    f1 = (
        2 * precision * cobertura / (precision + cobertura)
        if precision + cobertura > 0
        else 0.0
    )

    return {
        "precision": round(precision, 4),
        "cobertura": round(cobertura, 4),
        "f1": round(f1, 4)
    }


CASOS = [
    ("¿Qué es Python?", "Python es un lenguaje de programación."),
    ("¿Qué es una variable?", "Una variable almacena un valor."),
    ("¿Qué es una función?", "Una función es un bloque de código reutilizable."),
    ("¿Qué es una lista en Python?", "Una lista es una colección ordenada y mutable."),
    ("¿Qué es una tupla?", "Una tupla es una colección ordenada e inmutable."),
    ("¿Qué es un diccionario?", "Un diccionario almacena pares de clave y valor."),
    ("¿Qué es un bucle for?", "Un bucle for permite iterar sobre elementos."),
    ("¿Qué es un bucle while?", "Un bucle while repite instrucciones mientras una condición sea verdadera."),
    ("¿Qué es una clase?", "Una clase define atributos y métodos de objetos."),
    ("¿Qué es un objeto?", "Un objeto es una instancia de una clase."),
    ("¿Qué es una cadena de texto?", "Una cadena es una secuencia de caracteres."),
    ("¿Qué es un booleano?", "Un booleano representa verdadero o falso."),
    ("¿Qué es una excepción?", "Una excepción representa un error durante la ejecución."),
    ("¿Qué es un módulo?", "Un módulo es un archivo con código Python."),
    ("¿Qué es una biblioteca?", "Una biblioteca reúne módulos y funcionalidades reutilizables."),
    ("¿Qué es pip?", "Pip es un gestor de paquetes de Python."),
    ("¿Qué es pytest?", "Pytest es una herramienta para ejecutar pruebas en Python."),
    ("¿Qué es una API?", "Una API permite la comunicación entre aplicaciones."),
    ("¿Qué es JSON?", "JSON es un formato de intercambio de datos."),
    ("¿Qué es Git?", "Git es un sistema de control de versiones.")
]


def main():
    resultados = []

    print("INICIANDO EVALUACIÓN DE 20 RESPUESTAS")

    for numero, (consulta, referencia) in enumerate(CASOS, 1):
        print(f"\nProcesando caso {numero}/20...")

        try:
            respuesta = consultar_modelo(
                consulta + " Responde en una oración breve."
            )

            metricas = calcular_metricas(
                referencia, respuesta
            )

            registro = {
                "id": numero,
                "consulta": consulta,
                "referencia": referencia,
                "respuesta": respuesta,
                **metricas
            }

            resultados.append(registro)

            print(f"F1: {metricas['f1']:.2f}")

        except Exception as error:
            print(f"Error en caso {numero}: {error}")

    archivo = BASE_DIR / "resultados_metricas.json"

    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(
            resultados,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"\nRespuestas guardadas: {len(resultados)}/20")
    print(f"Archivo: {archivo}")


if __name__ == "__main__":
    main()
