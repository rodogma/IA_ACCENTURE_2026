
import sys
import time
from pathlib import Path

import requests

# Permitir importar el módulo del Bloque 7
raiz = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(raiz / "Modulo_1" / "Bloque_7"))

from consumir_api_comparar import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    calcular_costo
)


# Precios en USD por token
# Nivel de pago estándar, octubre de 2026
MODELOS = {
    "gemini-3.5-flash-lite": {
        "entrada": 0.30 / 1_000_000,
        "salida": 2.50 / 1_000_000
    },
    "gemini-3.6-flash": {
        "entrada": 0.75 / 1_000_000,
        "salida": 3.75 / 1_000_000
    }
}

PREGUNTA = "¿Cuál es la capital de Inglaterra?"
REPETICIONES = 4


def probar_modelo(modelo, precios):
    print(f"\n{'=' * 55}")
    print(f"MODELO: {modelo}")
    print(f"{'=' * 55}")

    latencias = []
    costos = []
    respuestas = []

    for i in range(REPETICIONES):
        try:
            url, body, headers = armar_peticion(
                PREGUNTA,
                modelo
            )

            inicio = time.perf_counter()

            datos = enviar_peticion(
                url, body, headers
            )

            fin = time.perf_counter()

            duracion = fin - inicio

            texto = extraer_texto(datos)

            costo = calcular_costo(
                datos,
                precios["entrada"],
                precios["salida"]
            )

            uso = datos.get("usageMetadata", {})

            latencias.append(duracion)
            costos.append(costo)
            respuestas.append(texto)

            print(f"\nIntento {i + 1}:")
            print(f"Latencia: {duracion:.2f} segundos")
            print(f"Tokens entrada: {uso.get('promptTokenCount', 0)}")
            print(f"Tokens totales: {uso.get('totalTokenCount', 0)}")
            print(f"Costo estimado: USD {costo:.8f}")
            print(f"Respuesta: {texto[:200]}")

        except requests.exceptions.HTTPError as error:
            print(f"\nIntento {i + 1}: Error HTTP")
            print("Código:", error.response.status_code)
            print("Detalle:", error.response.text[:300])

        except requests.exceptions.RequestException as error:
            print(f"\nIntento {i + 1}: Error de conexión")
            print(error)

        except (TypeError, ValueError) as error:
            print(f"\nIntento {i + 1}: Error de datos")
            print(error)

    if not latencias:
        print("\nNo hubo peticiones exitosas.")
        return None

    promedio = sum(latencias) / len(latencias)
    costo_total = sum(costos)

    print(f"\n--- RESUMEN: {modelo} ---")
    print(f"Pruebas exitosas: {len(latencias)}/{REPETICIONES}")
    print(f"Latencia promedio: {promedio:.2f} segundos")
    print(f"Costo total estimado: USD {costo_total:.8f}")

    return {
        "modelo": modelo,
        "latencia": promedio,
        "costo": costo_total,
        "exitosas": len(latencias),
        "respuestas": respuestas
    }


def main():
    resultados = []

    for modelo, precios in MODELOS.items():
        resultado = probar_modelo(modelo, precios)

        if resultado:
            resultados.append(resultado)

    print("\n" + "=" * 55)
    print("COMPARACIÓN FINAL")
    print("=" * 55)

    for resultado in resultados:
        print(f"\nModelo: {resultado['modelo']}")
        print(f"Latencia: {resultado['latencia']:.2f} s")
        print(f"Costo estimado: USD {resultado['costo']:.8f}")

    print("\nEvalúa manualmente la calidad de las respuestas.")


if __name__ == "__main__":
    main()
