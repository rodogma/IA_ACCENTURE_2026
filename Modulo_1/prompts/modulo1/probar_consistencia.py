
"""


Ejecutar desde la raíz del proyecto:
python Modulo_1/prompts/modulo1/probar_consistencia.py
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


# =====================================================
# 1. CONFIGURACIÓN DE RUTAS
# =====================================================

RAIZ = Path(__file__).resolve().parents[3]

CARPETA_PROMPTS = RAIZ / "Modulo_1" / "prompts"

CARPETA_MODULO = CARPETA_PROMPTS / "modulo1"

RUTA_ENV = RAIZ / ".env"

SALIDA = CARPETA_PROMPTS / "registro_resultados.json"


# =====================================================
# 2. CARGAR VARIABLES DE ENTORNO
# =====================================================

if not RUTA_ENV.is_file():
    raise FileNotFoundError(
        f"No se encontró el archivo .env en: {RUTA_ENV}"
    )

load_dotenv(dotenv_path=RUTA_ENV)


# =====================================================
# 3. IMPORTAR FUNCIONES Y BANCO DE PROMPTS
# =====================================================

sys.path.insert(0, str(CARPETA_PROMPTS))
sys.path.insert(0, str(CARPETA_MODULO))

from banco_prompts import BANCO_DE_PROMPTS

from cliente_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
    MODELO
)


# =====================================================
# 4. CONFIGURACIÓN DE PRUEBAS
# =====================================================

REPETICIONES = 3

ESPERA_SEGUNDOS = 2


# =====================================================
# 5. VALIDAR ESTRUCTURA JSON
# =====================================================

def validar_estructura(datos, prompt):

    if not isinstance(datos, dict):
        raise ValueError(
            "La respuesta JSON debe ser un objeto."
        )

    for clave, tipo in prompt["claves_esperadas"].items():

        if clave not in datos:
            raise ValueError(
                f"Falta la clave '{clave}'."
            )

        valor = datos[clave]

        if tipo is float:

            if isinstance(valor, bool) or not isinstance(
                valor, (int, float)
            ):
                raise ValueError(
                    f"'{clave}' debe ser numérico."
                )

        elif tipo is int:

            if isinstance(valor, bool) or not isinstance(
                valor, int
            ):
                raise ValueError(
                    f"'{clave}' debe ser un entero."
                )

        elif not isinstance(valor, tipo):

            raise ValueError(
                f"'{clave}' tiene un tipo incorrecto."
            )

    # Validar sentimiento
    if "sentimiento" in datos:

        if datos["sentimiento"] not in (
            "positivo",
            "negativo",
            "neutro"
        ):
            raise ValueError(
                "El sentimiento no es válido."
            )

    # Validar confianza
    if "confianza" in datos:

        if not 0 <= datos["confianza"] <= 1:
            raise ValueError(
                "La confianza debe estar entre 0 y 1."
            )

    # Validar lugares
    if "lugares" in datos:

        if not isinstance(datos["lugares"], list):
            raise ValueError(
                "'lugares' debe ser una lista."
            )

        if not all(
            isinstance(elemento, str)
            for elemento in datos["lugares"]
        ):
            raise ValueError(
                "Todos los lugares deben ser textos."
            )

    return True


# =====================================================
# 6. GUARDAR REGISTRO JSON
# =====================================================

def guardar_registro(registro):

    SALIDA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        SALIDA,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            registro,
            archivo,
            indent=2,
            ensure_ascii=False
        )


# =====================================================
# 7. EJECUTAR PRUEBAS
# =====================================================

def ejecutar():

    print("=" * 60)
    print("BANCO DE PROMPTS - VALIDACIÓN DE CONSISTENCIA")
    print("=" * 60)

    print(f"Modelo: {MODELO}")
    print(f"Prompts disponibles: {len(BANCO_DE_PROMPTS)}")
    print(f"Repeticiones por prompt: {REPETICIONES}")

    registro = {
        "modelo": MODELO,
        "fecha_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "repeticiones_por_prompt": REPETICIONES,
        "resultados": {}
    }

    for prompt in BANCO_DE_PROMPTS:

        nombre = prompt["nombre"]

        exitos = 0
        fallos = []
        respuestas_validas = []

        print("\n" + "=" * 60)
        print(f"PROBANDO: {nombre}")
        print("=" * 60)

        print("Entrada del usuario:")
        print(prompt["ejemplo_usuario"])

        for intento in range(1, REPETICIONES + 1):

            print(f"\n--- INTENTO {intento} ---")

            try:

                # 1. Preparar petición
                url, body, headers = armar_peticion(
                    prompt["ejemplo_usuario"],
                    prompt["system_instruction"],
                    prompt.get("response_schema")
                )

                # 2. Enviar petición a Gemini
                respuesta = enviar_peticion(
                    url,
                    body,
                    headers
                )

                # 3. Extraer texto generado
                texto = extraer_texto(respuesta)

                # 4. Convertir respuesta a JSON
                datos = parsear_respuesta_json(texto)

                # 5. Validar JSON y estructura
                validar_estructura(datos, prompt)

                # 6. Contabilizar éxito
                exitos += 1

                respuestas_validas.append({
                    "intento": intento,
                    "respuesta": datos
                })

                # 7. Mostrar respuesta real
                print("Estado: JSON válido")
                print("Estructura: Correcta")

                print("\nRespuesta de Gemini:")
                print(
                    json.dumps(
                        datos,
                        indent=2,
                        ensure_ascii=False
                    )
                )

            except requests.exceptions.Timeout:

                detalle = (
                    "Timeout: Gemini tardó demasiado en responder."
                )

                print("Estado: FALLÓ")
                print("Motivo:", detalle)

                fallos.append({
                    "intento": intento,
                    "motivo": detalle
                })

            except requests.exceptions.RequestException as error:

                detalle = (
                    f"{type(error).__name__}: {error}"
                )

                print("Estado: FALLÓ")
                print("Motivo:", detalle)

                fallos.append({
                    "intento": intento,
                    "motivo": detalle
                })

            except (
                ValueError,
                TypeError,
                KeyError,
                IndexError
            ) as error:

                detalle = (
                    f"{type(error).__name__}: {error}"
                )

                print("Estado: FALLÓ")
                print("Motivo:", detalle)

                fallos.append({
                    "intento": intento,
                    "motivo": detalle
                })

            # Pausa entre intentos
            if intento < REPETICIONES:
                time.sleep(ESPERA_SEGUNDOS)

        # =================================================
        # 8. RESULTADOS DEL PROMPT
        # =================================================

        total_fallos = REPETICIONES - exitos

        porcentaje = round(
            (exitos / REPETICIONES) * 100,
            2
        )

        registro["resultados"][nombre] = {
            "exitos": exitos,
            "intentos": REPETICIONES,
            "fallos": total_fallos,
            "tasa_consistencia_pct": porcentaje,
            "respuestas_validas": respuestas_validas,
            "detalle_fallos": fallos
        }

        print("\n" + "-" * 60)
        print(f"RESUMEN: {nombre}")
        print("-" * 60)

        print(f"Intentos: {REPETICIONES}")
        print(f"Respuestas válidas: {exitos}")
        print(f"Respuestas fallidas: {total_fallos}")
        print(f"Consistencia estructural: {porcentaje:.2f}%")

        # Guardar después de cada prompt
        guardar_registro(registro)

    # =====================================================
    # 9. RESUMEN GENERAL
    # =====================================================

    total_intentos = sum(
        resultado["intentos"]
        for resultado in registro["resultados"].values()
    )

    total_exitos = sum(
        resultado["exitos"]
        for resultado in registro["resultados"].values()
    )

    porcentaje_general = round(
        total_exitos / total_intentos * 100,
        2
    ) if total_intentos else 0

    print("\n" + "=" * 60)
    print("RESULTADO GENERAL")
    print("=" * 60)

    for nombre, resultado in registro["resultados"].items():
        print(
            f"{nombre}: "
            f"{resultado['exitos']}/"
            f"{resultado['intentos']} "
            f"({resultado['tasa_consistencia_pct']:.2f}%)"
        )

    print("\nTotal de pruebas:", total_intentos)
    print("Respuestas válidas:", total_exitos)
    print(f"Consistencia general: {porcentaje_general:.2f}%")

    registro["resumen_general"] = {
        "total_intentos": total_intentos,
        "total_exitos": total_exitos,
        "total_fallos": total_intentos - total_exitos,
        "tasa_consistencia_pct": porcentaje_general
    }

    guardar_registro(registro)

    print("\nRegistro guardado en:")
    print(SALIDA)


# =====================================================
# 10. EJECUCIÓN PRINCIPAL
# =====================================================

if __name__ == "__main__":
    ejecutar()
