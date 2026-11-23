
import sys
import time
import msvcrt

from datetime import datetime
from langchain_core.tools import tool


# ==========================================
# 1. REGISTRO DE APROBACIONES
# ==========================================

registro_aprobaciones = []


# ==========================================
# 2. ESPERAR APROBACIÓN HUMANA
# ==========================================

def esperar_aprobacion(
    mensaje: str,
    tiempo_limite_segundos: int = 300,
) -> bool:
    """
    Espera una aprobación humana en Windows.

    El usuario debe presionar S para aprobar
    o N para rechazar.

    Si vence el tiempo, se rechaza.
    """

    print("\n" + "=" * 50)
    print("SOLICITUD DE APROBACIÓN HUMANA")
    print("=" * 50)

    print(mensaje)
    print("Presiona S para aprobar o N para rechazar.")
    print(
        f"Tiempo máximo: "
        f"{tiempo_limite_segundos} segundos."
    )

    # Eliminar teclas pendientes del búfer
    while msvcrt.kbhit():
        msvcrt.getwch()

    inicio = time.monotonic()

    while (
        time.monotonic() - inicio
        < tiempo_limite_segundos
    ):

        if msvcrt.kbhit():

            tecla = msvcrt.getwch().lower()

            if tecla == "s":
                print("\nAPROBACIÓN CONCEDIDA")
                return True

            if tecla == "n":
                print("\nAPROBACIÓN RECHAZADA")
                return False

            print(
                "\nOpción no válida. "
                "Presiona S o N."
            )

        time.sleep(0.1)

    print("\nTIEMPO AGOTADO")
    print("La operación fue rechazada.")

    return False


# ==========================================
# 3. REGISTRAR DECISIONES
# ==========================================

def registrar_aprobacion(
    herramienta: str,
    argumentos: dict,
    aprobado: bool,
) -> None:

    registro_aprobaciones.append({
        "herramienta": herramienta,
        "argumentos": argumentos,
        "aprobado": aprobado,
        "momento": datetime.now().isoformat(),
    })


# ==========================================
# 4. HERRAMIENTA DE REEMBOLSO
# ==========================================

@tool
def generar_reembolso(
    numero_pedido: str,
    monto: float,
) -> str:
    """
    Simula la generación de un reembolso.

    Usar cuando se solicita reembolsar un pedido.
    Requiere aprobación humana antes de continuar.

    Esta herramienta es una demostración:
    no transfiere dinero ni ejecuta pagos reales.
    """

    if monto <= 0:
        return (
            "Error: el monto del reembolso "
            "debe ser mayor que cero."
        )

    mensaje = (
        f"El agente solicita reembolsar "
        f"${monto:,.2f} para el pedido "
        f"{numero_pedido}."
    )

    aprobado = esperar_aprobacion(
        mensaje,
        tiempo_limite_segundos=300,
    )

    registrar_aprobacion(
        herramienta="generar_reembolso",
        argumentos={
            "numero_pedido": numero_pedido,
            "monto": monto,
        },
        aprobado=aprobado,
    )

    if not aprobado:
        return (
            f"Reembolso del pedido {numero_pedido} "
            "NO autorizado por el supervisor humano."
        )

    return (
        f"Reembolso simulado de ${monto:,.2f} "
        f"para el pedido {numero_pedido}. "
        "Autorizado por el supervisor humano."
    )


# ==========================================
# 5. PROGRAMA PRINCIPAL
# ==========================================

def main():

    print("\n========================================")
    print("BLOQUE 23 - APROBACIÓN HUMANA")
    print("========================================")

    resultado = generar_reembolso.invoke({
        "numero_pedido": "PED789",
        "monto": 1500.0,
    })

    print("\nRESULTADO:")
    print(resultado)

    print("\nREGISTRO DE APROBACIONES:")

    for registro in registro_aprobaciones:
        print(registro)

    print("\n========================================")
    print("FIN DEL PROGRAMA")
    print("========================================")


if __name__ == "__main__":
    main()
