
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def preguntar(mensaje):
    while True:
        valor = input(mensaje + " (si/no): ").strip().lower()

        if valor in ("si", "sí"):
            return "si"

        if valor == "no":
            return "no"

        print("Escribe si o no.")


def guardar_revision(destino, revision_manual):
    temporal = destino.with_suffix(".tmp")

    with open(temporal, "w", encoding="utf-8") as f:
        json.dump(
            revision_manual,
            f,
            indent=2,
            ensure_ascii=False
        )

    temporal.replace(destino)


def main():
    archivo = BASE_DIR / "resultados_metricas.json"
    destino = BASE_DIR / "revision_manual.json"

    if not archivo.exists():
        print("Primero ejecuta evaluacion_bloque17.py")
        return

    with open(archivo, encoding="utf-8") as f:
        resultados = json.load(f)

    if len(resultados) < 20:
        print("Necesitas al menos 20 respuestas.")
        return

    ordenados = sorted(
        resultados,
        key=lambda caso: caso["f1"]
    )

    muestra = ordenados[:5] + ordenados[-5:]

    # Recuperar revisiones guardadas anteriormente
    if destino.exists():
        try:
            with open(destino, encoding="utf-8") as f:
                revision_manual = json.load(f)

            if not isinstance(revision_manual, list):
                print("El archivo de revisión no contiene una lista.")
                return

        except (json.JSONDecodeError, OSError) as error:
            print("No se pudo leer la revisión anterior:", error)
            print("No se sobrescribirá el archivo.")
            return
    else:
        revision_manual = []

    revisados = {
        caso["id"] for caso in revision_manual
    }

    print("\nINICIANDO REVISIÓN MANUAL")
    print(f"Casos recuperados: {len(revisados)}")

    for caso in muestra:

        if caso["id"] in revisados:
            print(f"Caso {caso['id']}: YA REVISADO")
            continue

        print("\n" + "=" * 60)
        print("CASO:", caso["id"])
        print("CONSULTA:", caso["consulta"])
        print("REFERENCIA:", caso["referencia"])
        print("RESPUESTA:", caso["respuesta"])
        print("F1:", caso["f1"])
        print("=" * 60)

        correccion = preguntar(
            "¿La respuesta es factualmente correcta?"
        )

        completitud = preguntar(
            "¿La respuesta está completa?"
        )

        contradiccion = preguntar(
            "¿Contradice la referencia?"
        )

        while True:
            nota = input(
                "Escribe una explicación de tu evaluación: "
            ).strip()

            if nota:
                break

            print("Debes escribir una explicación.")

        registro = {
            "id": caso["id"],
            "consulta": caso["consulta"],
            "referencia": caso["referencia"],
            "respuesta": caso["respuesta"],
            "f1": caso["f1"],
            "correccion_factual": correccion,
            "completitud": completitud,
            "contradiccion": contradiccion,
            "nota": nota
        }

        revision_manual.append(registro)

        try:
            guardar_revision(destino, revision_manual)

        except OSError as error:
            revision_manual.pop()
            print("\nERROR AL GUARDAR:", error)
            print("Libera espacio en disco y vuelve a ejecutar.")
            return

        revisados.add(caso["id"])

        print("Evaluación guardada correctamente.")
        print(f"Progreso: {len(revisados)}/10")

    print("\n" + "=" * 60)
    print("REVISIÓN MANUAL COMPLETADA")
    print(f"Casos revisados: {len(revisados)}/10")
    print("Archivo:", destino)


if __name__ == "__main__":
    main()
