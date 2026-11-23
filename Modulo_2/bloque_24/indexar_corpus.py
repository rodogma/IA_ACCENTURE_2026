
import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


# ==========================================
# 1. CONFIGURACIÓN DEL PROYECTO
# ==========================================

RUTA_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_BLOQUE = Path(__file__).resolve().parent
RUTA_VECTORSTORE = RUTA_BLOQUE / "vectorstore"

load_dotenv(RUTA_PROYECTO / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "No se encontró GEMINI_API_KEY. "
        "Revisa el archivo .env del proyecto."
    )


# ==========================================
# 2. CORPUS DE CINCO DOCUMENTOS
# ==========================================

corpus = [
    Document(
        page_content=(
            "El agente recomienda excavadoras, bulldozers "
            "y motoniveladoras para trabajos de movimiento "
            "de tierra y nivelación de terrenos."
        ),
        metadata={"fuente": "maquinaria", "documento": 1},
    ),

    Document(
        page_content=(
            "Para construir cimientos se utilizan equipos "
            "de perforación de pilotes y grúas. "
            "La maquinaria depende de las características "
            "del suelo y del proyecto."
        ),
        metadata={"fuente": "cimentacion", "documento": 2},
    ),

    Document(
        page_content=(
            "El agente utiliza herramientas de LangChain "
            "para seleccionar maquinaria según la actividad "
            "solicitada por el usuario."
        ),
        metadata={"fuente": "agente", "documento": 3},
    ),

    Document(
        page_content=(
            "El agente con memoria utiliza "
            "RunnableWithMessageHistory para conservar "
            "el historial de conversación de una sesión."
        ),
        metadata={"fuente": "memoria", "documento": 4},
    ),

    Document(
        page_content=(
            "Las operaciones sensibles, como generar "
            "reembolsos, requieren aprobación humana. "
            "Cada decisión debe registrarse para "
            "permitir su revisión."
        ),
        metadata={"fuente": "aprobaciones", "documento": 5},
    ),
]


# ==========================================
# 3. CHUNKING
# ==========================================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=250,
    chunk_overlap=30,
)

chunks = splitter.split_documents(corpus)

print("\n========================================")
print("BLOQUE 24 - INDEXACIÓN DEL CORPUS")
print("========================================")

print(f"\nDocumentos originales: {len(corpus)}")
print(f"Chunks generados: {len(chunks)}")

for numero, chunk in enumerate(chunks, start=1):
    print(f"\nChunk {numero}:")
    print(chunk.page_content)
    print("Metadata:", chunk.metadata)


# ==========================================
# 4. EMBEDDINGS REALES CON GEMINI
# ==========================================

print("\nConectando con Gemini Embeddings...")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=API_KEY,
)


# ==========================================
# 5. PERSISTENCIA EN CHROMA
# ==========================================

print("\nIndexando documentos en Chroma...")

# Evita duplicados si ejecutas el script otra vez.
# Conserva la colección existente y actualiza
# los documentos con los mismos identificadores.

vectorstore = Chroma(
    collection_name="corpus_bloque_24",
    embedding_function=embeddings,
    persist_directory=str(RUTA_VECTORSTORE),
)

ids = [
    f"documento_{chunk.metadata['documento']}_chunk_{indice}"
    for indice, chunk in enumerate(chunks)
]

vectorstore.add_documents(
    documents=chunks,
    ids=ids,
)

print("\n========================================")
print("INDEXACIÓN COMPLETADA")
print("========================================")

print(f"Chunks indexados en esta ejecución: {len(chunks)}")
print(f"Total de registros: {vectorstore._collection.count()}")
print(f"Carpeta: {RUTA_VECTORSTORE}")
print("\nLos embeddings quedaron persistidos en disco.")
