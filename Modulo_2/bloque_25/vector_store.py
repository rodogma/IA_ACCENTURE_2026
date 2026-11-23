
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


# ==========================================
# BLOQUE 25 - VECTOR STORE CON CHROMA
# ==========================================


# 1. RUTAS DEL PROYECTO

RUTA_PROYECTO = Path(__file__).resolve().parents[2]

RUTA_BLOQUE_24 = (
    RUTA_PROYECTO / "Modulo_2" / "bloque_24"
)

RUTA_VECTORSTORE = RUTA_BLOQUE_24 / "vectorstore"

NOMBRE_COLECCION = "corpus_bloque_24"


# ==========================================
# 2. CARGAR VARIABLES DE ENTORNO
# ==========================================

load_dotenv(RUTA_PROYECTO / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "ERROR: No se encontró GEMINI_API_KEY "
        "en el archivo .env"
    )


# ==========================================
# 3. CONFIGURAR EMBEDDINGS DE GEMINI
# ==========================================

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=API_KEY,
)


# ==========================================
# 4. FUNCIÓN DE REINTENTOS
# ==========================================

def con_reintentos(
    operacion,
    max_intentos=4,
    espera_inicial=5,
):
    espera = espera_inicial

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

            if not error_temporal:
                raise

            if intento == max_intentos:
                print(
                    "\nERROR: Se agotaron "
                    "los intentos de conexión."
                )
                raise

            print(
                f"\nGemini no está disponible. "
                f"Reintentando en {espera} segundos..."
            )

            time.sleep(espera)

            espera *= 2


# ==========================================
# 5. ABRIR BASE DE DATOS EXISTENTE
# ==========================================

def cargar_vectorstore():

    print("\n========================================")
    print("BLOQUE 25 - VECTOR STORE")
    print("========================================")

    print("\nRuta:", RUTA_VECTORSTORE)
    print("Colección:", NOMBRE_COLECCION)

    if not RUTA_VECTORSTORE.exists():
        raise FileNotFoundError(
            "\nNo existe el vectorstore del Bloque 24.\n"
            "Primero ejecuta:\n"
            "python Modulo_2/bloque_24/indexar_corpus.py"
        )

    # No crear una colección vacía por accidente.
    vectorstore = Chroma(
        collection_name=NOMBRE_COLECCION,
        embedding_function=embeddings,
        persist_directory=str(RUTA_VECTORSTORE),
        create_collection_if_not_exists=False,
    )

    cantidad = vectorstore._collection.count()

    print("\nChunks almacenados:", cantidad)

    if cantidad == 0:
        raise ValueError(
            "La colección existe, pero está vacía. "
            "Ejecuta primero la indexación del Bloque 24."
        )

    print("\nVECTOR STORE CARGADO CORRECTAMENTE")

    return vectorstore


# ==========================================
# 6. MOSTRAR DOCUMENTOS GUARDADOS
# ==========================================

def mostrar_documentos(vectorstore):

    print("\n========================================")
    print("DOCUMENTOS ALMACENADOS")
    print("========================================")

    registros = vectorstore.get(
        include=["documents", "metadatas"]
    )

    documentos = registros["documents"]
    metadatas = registros["metadatas"]

    for numero, (texto, metadata) in enumerate(
        zip(documentos, metadatas),
        start=1,
    ):

        print(f"\nDocumento {numero}:")
        print(texto)
        print("Metadata:", metadata)


# ==========================================
# 7. BÚSQUEDA SEMÁNTICA
# ==========================================

def buscar_documentos(vectorstore, pregunta):

    print("\n========================================")
    print("BÚSQUEDA SEMÁNTICA")
    print("========================================")

    print("\nPregunta:", pregunta)

    cantidad = vectorstore._collection.count()

    resultados = con_reintentos(
        lambda: vectorstore.similarity_search(
            query=pregunta,
            k=min(3, cantidad),
        )
    )

    if not resultados:
        print("\nNo se encontraron documentos.")
        return

    for numero, documento in enumerate(
        resultados,
        start=1,
    ):

        print(f"\nRESULTADO {numero}")
        print("Contenido:", documento.page_content)
        print("Metadata:", documento.metadata)


# ==========================================
# 8. PROGRAMA PRINCIPAL
# ==========================================

def main():

    try:
        vectorstore = cargar_vectorstore()

        mostrar_documentos(vectorstore)

        pregunta = (
            "¿Qué maquinaria necesito "
            "para nivelar un terreno?"
        )

        buscar_documentos(
            vectorstore,
            pregunta,
        )

        print("\n========================================")
        print("BLOQUE 25 EJECUTADO CORRECTAMENTE")
        print("========================================")

    except Exception as error:

        print("\n========================================")
        print("ERROR EN BLOQUE 25")
        print("========================================")

        print(type(error).__name__)
        print(error)


if __name__ == "__main__":
    main()
