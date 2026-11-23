
import os
import time
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


# ==================================================
# BLOQUE 27 - EVALUACION DE RECUPERACION
# PRECISION@K Y RECALL@K
# ==================================================


# ==================================================
# 1. CONFIGURACION
# ==================================================

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
CARPETA_BLOQUE = Path(__file__).resolve().parent

load_dotenv(RAIZ_PROYECTO / ".env")

API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

if not API_KEY:
    raise ValueError(
        "No se encontro GEMINI_API_KEY en el archivo .env"
    )

RUTA_VECTORSTORE = (
    RAIZ_PROYECTO
    / "Modulo_2"
    / "bloque_24"
    / "vectorstore"
)

NOMBRE_COLECCION = "corpus_bloque_24"

K = 3

# Configuracion utilizada en el Bloque 24
CHUNK_SIZE = 250
CHUNK_OVERLAP = 30

RUTA_RESULTADOS = (
    CARPETA_BLOQUE / "resultados_evaluacion1.txt"
)


# ==================================================
# 2. REINTENTOS PARA ERRORES TEMPORALES
# ==================================================

def con_reintentos(operacion, max_intentos=4):

    espera = 5

    for intento in range(1, max_intentos + 1):

        try:
            return operacion()

        except Exception as error:

            mensaje = str(error).lower()

            error_temporal = any(
                codigo in mensaje
                for codigo in [
                    "429",
                    "resource_exhausted",
                    "503",
                    "unavailable",
                    "timeout",
                ]
            )

            if not error_temporal or intento == max_intentos:
                raise

            print(
                f"\nError temporal de Gemini. "
                f"Reintentando en {espera} segundos..."
            )

            time.sleep(espera)
            espera *= 2


# ==================================================
# 3. CARGAR VECTORSTORE EXISTENTE
# ==================================================

def cargar_vectorstore():

    if not RUTA_VECTORSTORE.exists():
        raise FileNotFoundError(
            f"No existe el indice:\n{RUTA_VECTORSTORE}\n"
            "Ejecuta primero el indexador del Bloque 24."
        )

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=API_KEY,
    )

    vectorstore = Chroma(
        collection_name=NOMBRE_COLECCION,
        persist_directory=str(RUTA_VECTORSTORE),
        embedding_function=embeddings,
        create_collection_if_not_exists=False,
    )

    cantidad = vectorstore._collection.count()

    if cantidad == 0:
        raise ValueError(
            "La coleccion esta vacia. "
            "Debes indexar primero el corpus."
        )

    print("\nColeccion:", NOMBRE_COLECCION)
    print("Chunks almacenados:", cantidad)

    return vectorstore


# ==================================================
# 4. MOSTRAR IDS Y DOCUMENTOS
# ==================================================

def mostrar_documentos(vectorstore):

    registros = vectorstore.get(
        include=["documents", "metadatas"]
    )

    print("\n========================================")
    print("IDS Y DOCUMENTOS DEL INDICE")
    print("========================================")

    for identificador, contenido, metadata in zip(
        registros["ids"],
        registros["documents"],
        registros["metadatas"],
    ):

        print("\nID:", identificador)
        print("Contenido:", contenido)
        print("Metadata:", metadata)

    return registros


# ==================================================
# 5. CASOS DE EVALUACION
# IDS REALES DEL BLOQUE 24
# ==================================================

# Estos IDs se identificaron leyendo el contenido
# original de los cinco documentos del indice.
#
# No fueron seleccionados usando los resultados
# del retriever.

casos_evaluacion = [

    {
        "pregunta": "¿Que maquinaria sirve para nivelar terrenos?",
        "ids_relevantes": {"documento_1_chunk_0"},
    },

    {
        "pregunta": "¿Que equipo se utiliza para mover tierra?",
        "ids_relevantes": {"documento_1_chunk_0"},
    },

    {
        "pregunta": "¿Que maquinaria se usa para construir cimientos?",
        "ids_relevantes": {"documento_2_chunk_1"},
    },

    {
        "pregunta": "¿Como funciona un agente con herramientas?",
        "ids_relevantes": {"documento_3_chunk_2"},
    },

    {
        "pregunta": "¿Como elige un agente una herramienta?",
        "ids_relevantes": {"documento_3_chunk_2"},
    },

    {
        "pregunta": "¿Como recuerda un agente una conversacion?",
        "ids_relevantes": {"documento_4_chunk_3"},
    },

    {
        "pregunta": "¿Cuando se necesita aprobacion humana?",
        "ids_relevantes": {"documento_5_chunk_4"},
    },

    {
        "pregunta": "¿Como se controlan operaciones de riesgo?",
        "ids_relevantes": {"documento_5_chunk_4"},
    },

    {
        "pregunta": "¿Cual es la temperatura de Marte hoy?",
        "ids_relevantes": set(),
    },

]


# ==================================================
# 6. PRECISION@K
# ==================================================

def precision_at_k(ids_recuperados, ids_relevantes):

    if not ids_recuperados:
        return 0.0

    acertados = [
        identificador
        for identificador in ids_recuperados
        if identificador in ids_relevantes
    ]

    return len(acertados) / len(ids_recuperados)


# ==================================================
# 7. RECALL@K
# ==================================================

def recall_at_k(ids_recuperados, ids_relevantes):

    if not ids_relevantes:
        return None

    acertados = [
        identificador
        for identificador in ids_recuperados
        if identificador in ids_relevantes
    ]

    return len(acertados) / len(ids_relevantes)


# ==================================================
# 8. CALCULAR PROMEDIOS
# ==================================================

def promediar(valores):

    validos = [
        valor
        for valor in valores
        if valor is not None
    ]

    if not validos:
        return 0.0

    return sum(validos) / len(validos)


# ==================================================
# 9. EVALUAR RETRIEVER REAL
# ==================================================

def evaluar_recuperacion(vectorstore, casos, k=3):

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": k}
    )

    resultados = []

    for numero, caso in enumerate(
        casos,
        start=1,
    ):

        print("\n----------------------------------------")
        print(
            f"Evaluando pregunta {numero}/{len(casos)}"
        )
        print("----------------------------------------")

        print("Pregunta:", caso["pregunta"])

        chunks = con_reintentos(
            lambda: retriever.invoke(caso["pregunta"])
        )

        ids_recuperados = [
            documento.id
            for documento in chunks
        ][:k]

        if any(
            identificador is None
            for identificador in ids_recuperados
        ):
            raise ValueError(
                "Un documento recuperado no tiene ID. "
                "Revisa la indexacion del Bloque 24."
            )

        precision = precision_at_k(
            ids_recuperados,
            caso["ids_relevantes"],
        )

        recall = recall_at_k(
            ids_recuperados,
            caso["ids_relevantes"],
        )

        print("IDs relevantes:", caso["ids_relevantes"])
        print("IDs recuperados:", ids_recuperados)
        print(f"Precision@{k}: {precision:.2f}")

        if recall is None:
            print(f"Recall@{k}: n/a")
        else:
            print(f"Recall@{k}: {recall:.2f}")

        resultados.append(
            {
                "pregunta": caso["pregunta"],
                "ids_recuperados": ids_recuperados,
                "precision": precision,
                "recall": recall,
            }
        )

    precision_promedio = promediar(
        resultado["precision"]
        for resultado in resultados
    )

    recall_promedio = promediar(
        resultado["recall"]
        for resultado in resultados
    )

    return (
        resultados,
        precision_promedio,
        recall_promedio,
    )


# ==================================================
# 10. GUARDAR RESULTADOS EN TXT
# ==================================================

def guardar_resultados(
    resultados,
    precision_promedio,
    recall_promedio,
):

    with open(
        RUTA_RESULTADOS,
        "w",
        encoding="utf-8",
    ) as archivo:

        archivo.write(
            f"Fecha: "
            f"{datetime.now().isoformat(timespec='seconds')}\n"
        )

        archivo.write(
            f"Configuracion: k={K}, "
            f"chunk_size={CHUNK_SIZE}, "
            f"chunk_overlap={CHUNK_OVERLAP}\n\n"
        )

        for resultado in resultados:

            recall_texto = (
                "n/a"
                if resultado["recall"] is None
                else f"{resultado['recall']:.2f}"
            )

            archivo.write(
                f"{resultado['precision']:.2f}  "
                f"{recall_texto}  "
                f"{resultado['pregunta']}\n"
            )

        archivo.write(
            f"\npromedio -> "
            f"precision: {precision_promedio:.3f}  "
            f"recall: {recall_promedio:.3f}\n"
        )

    print("\nResultados guardados en:")
    print(RUTA_RESULTADOS)


# ==================================================
# 11. PROGRAMA PRINCIPAL
# ==================================================

def main():

    print("\n========================================")
    print("BLOQUE 27 - EVALUACION DE RECUPERACION")
    print("========================================")

    vectorstore = cargar_vectorstore()

    registros = mostrar_documentos(vectorstore)

    # Verificar que los IDs relevantes existen.

    ids_disponibles = set(registros["ids"])

    ids_etiquetados = set().union(
        *(
            caso["ids_relevantes"]
            for caso in casos_evaluacion
        )
    )

    ids_invalidos = (
        ids_etiquetados - ids_disponibles
    )

    if ids_invalidos:

        raise ValueError(
            "Hay IDs relevantes que no existen "
            f"en el indice: {sorted(ids_invalidos)}"
        )

    print("\n========================================")
    print("INICIANDO EVALUACION REAL")
    print("========================================")

    resultados, precision, recall = evaluar_recuperacion(
        vectorstore,
        casos_evaluacion,
        k=K,
    )

    print("\n========================================")
    print("RESULTADOS FINALES")
    print("========================================")

    for resultado in resultados:

        recall_texto = (
            "n/a"
            if resultado["recall"] is None
            else f"{resultado['recall']:.2f}"
        )

        print(
            f"{resultado['precision']:.2f}  "
            f"{recall_texto}  "
            f"{resultado['pregunta']}"
        )

    print(
        f"\npromedio -> "
        f"precision: {precision:.3f}  "
        f"recall: {recall:.3f}"
    )

    guardar_resultados(
        resultados,
        precision,
        recall,
    )

    print("\n========================================")
    print("BLOQUE 27 FINALIZADO CORRECTAMENTE")
    print("========================================")


if __name__ == "__main__":
    main()
