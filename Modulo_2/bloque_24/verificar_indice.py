
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

RUTA_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_BLOQUE = Path(__file__).resolve().parent
RUTA_VECTORSTORE = RUTA_BLOQUE / "vectorstore"

load_dotenv(RUTA_PROYECTO / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Falta GEMINI_API_KEY en .env")

if not RUTA_VECTORSTORE.exists():
    raise FileNotFoundError(
        "No existe la carpeta vectorstore. "
        "Ejecuta primero indexar_corpus.py."
    )


# ==========================================
# 2. RECONECTAR AL VECTOR STORE
# ==========================================

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=API_KEY,
)

vectorstore = Chroma(
    collection_name="corpus_bloque_24",
    embedding_function=embeddings,
    persist_directory=str(RUTA_VECTORSTORE),
)


# ==========================================
# 3. COMPROBAR PERSISTENCIA
# ==========================================

cantidad = vectorstore._collection.count()

print("\n========================================")
print("BLOQUE 24 - VERIFICACIÓN DE PERSISTENCIA")
print("========================================")

print(f"\nCarpeta: {RUTA_VECTORSTORE}")
print(f"Chunks recuperados: {cantidad}")

if cantidad == 0:
    print("\nERROR: La colección está vacía.")

else:
    print("\nPERSISTENCIA VERIFICADA CORRECTAMENTE")

    # Obtiene documentos ya almacenados.
    # No recalcula embeddings.
    registros = vectorstore.get(
        include=["documents", "metadatas"]
    )

    for numero, (texto, metadata) in enumerate(
        zip(
            registros["documents"],
            registros["metadatas"],
        ),
        start=1,
    ):
        print(f"\nDocumento almacenado {numero}:")
        print(texto)
        print("Metadata:", metadata)
