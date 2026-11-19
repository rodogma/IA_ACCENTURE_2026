# ==========================================================
# BLOQUE 28 - REGISTRO DE LATENCIA Y COSTO RAG
# ==========================================================

import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone

import chromadb
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

BASE = Path(__file__).resolve().parent
RAIZ = BASE.parent.parent
REGISTROS = BASE / "registros_latencia_costo.jsonl"
CARPETA_NUEVA = BASE / "vectorstore"
CARPETA_DOCUMENTOS = BASE / "documentos"
MODELO_EMBEDDING = "models/gemini-embedding-001"
MODELO_CHAT = "gemini-3.1-flash-lite"
COLECCION_NUEVA = "rag_bloque_28"

# Tarifas de referencia en USD por millon de tokens (generacion).
# Verifica precios actuales y modalidad en https://ai.google.dev/gemini-api/docs/pricing
# Pueden sobrescribirse en .env. No incluye costo de embeddings.
PRECIO_ENTRADA_MILLON_USD = 0.25
PRECIO_SALIDA_MILLON_USD = 1.50


def configurar():
    global MODELO_CHAT, MODELO_EMBEDDING
    for ruta in (BASE / ".env", RAIZ / ".env"):
        if ruta.is_file():
            load_dotenv(ruta, override=True)
            print("Archivo .env encontrado:", ruta)
            break

    # Coincide con la prioridad que usa la integracion de Gemini.
    clave = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not clave:
        raise RuntimeError("No se encontro GOOGLE_API_KEY ni GEMINI_API_KEY en .env")
    os.environ["GOOGLE_API_KEY"] = clave
    MODELO_CHAT = os.getenv("GEMINI_MODEL", MODELO_CHAT)
    MODELO_EMBEDDING = os.getenv("GEMINI_EMBEDDING_MODEL", MODELO_EMBEDDING)
    print("API Key: detectada")
    print("Modelo Gemini:", MODELO_CHAT)
    print("Modelo embeddings:", MODELO_EMBEDDING)
    print("Tarifas generacion USD/millon: entrada=", tarifa("PRECIO_ENTRADA_MILLON_USD", PRECIO_ENTRADA_MILLON_USD),
          "salida=", tarifa("PRECIO_SALIDA_MILLON_USD", PRECIO_SALIDA_MILLON_USD))


def tarifa(nombre, predeterminada):
    valor = os.getenv(nombre)
    if valor is None or not valor.strip():
        return predeterminada
    try:
        precio = float(valor)
    except ValueError as exc:
        raise ValueError(f"{nombre} debe ser un numero, no {valor!r}") from exc
    if precio < 0:
        raise ValueError(f"{nombre} no puede ser negativo")
    return precio


def buscar_vectorstore():
    print("\nBuscando base vectorial...")
    bases = sorted(BASE.parent.rglob("chroma.sqlite3"))
    bases += sorted(RAIZ.glob("vectorstore/chroma.sqlite3"))
    carpetas = list(dict.fromkeys(archivo.parent.resolve() for archivo in bases))
    carpetas.sort(key=lambda p: (p != CARPETA_NUEVA.resolve(), str(p)))
    disponibles = []
    for carpeta in carpetas:
        try:
            cliente = chromadb.PersistentClient(path=str(carpeta))
            for coleccion in cliente.list_collections():
                cantidad = coleccion.count()
                if cantidad > 0:
                    disponibles.append((carpeta, coleccion.name, cantidad))
        except Exception as error:
            print("No se pudo abrir:", carpeta, str(error))

    if disponibles:
        print("\nBases encontradas:")
        for indice, (ruta, nombre, cantidad) in enumerate(disponibles, 1):
            print(f"{indice}. {ruta} | coleccion={nombre} | documentos={cantidad}")
        if len(disponibles) > 1:
            seleccion = os.getenv("RAG_COLLECTION")
            if seleccion:
                coincidencias = [item for item in disponibles if item[1] == seleccion]
                if len(coincidencias) == 1:
                    return coincidencias[0][:2]
            raise RuntimeError("Hay varias colecciones Chroma. Define RAG_COLLECTION en .env y asegurate de que el nombre sea unico.")
        return disponibles[0][:2]
    return None


def cargar_documentos():
    if not CARPETA_DOCUMENTOS.is_dir():
        raise FileNotFoundError("No existe base Chroma con datos. Crea la carpeta 'documentos' y agrega archivos .txt, .md o .pdf.")
    documentos = []
    for archivo in sorted(CARPETA_DOCUMENTOS.rglob("*")):
        if not archivo.is_file():
            continue
        extension = archivo.suffix.lower()
        if extension in (".txt", ".md"):
            texto = archivo.read_text(encoding="utf-8-sig")
        elif extension == ".pdf":
            from pypdf import PdfReader
            lector = PdfReader(str(archivo))
            texto = "\n".join(pagina.extract_text() or "" for pagina in lector.pages)
        else:
            continue
        if texto.strip():
            documentos.append(Document(page_content=texto, metadata={"source": str(archivo)}))
    if not documentos:
        raise RuntimeError("No se encontraron documentos con texto extraible.")
    return documentos


def dividir_documentos(documentos):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    separador = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    return separador.split_documents(documentos)


def preparar_vectorstore(embeddings):
    encontrada = buscar_vectorstore()
    if encontrada:
        ruta, coleccion = encontrada
        print("\nUsando base existente:", ruta)
        print("Coleccion:", coleccion)
        print("IMPORTANTE: el modelo de embeddings debe coincidir con el de indexacion.")
        return Chroma(persist_directory=str(ruta), collection_name=coleccion, embedding_function=embeddings)

    print("\nNo existe una base Chroma con documentos. Creando desde 'documentos'...")
    fragmentos = dividir_documentos(cargar_documentos())
    print("Fragmentos para indexar:", len(fragmentos))
    CARPETA_NUEVA.mkdir(parents=True, exist_ok=True)
    base = Chroma(persist_directory=str(CARPETA_NUEVA), collection_name=COLECCION_NUEVA, embedding_function=embeddings)
    base.add_documents(fragmentos)
    print("Base vectorial creada correctamente")
    return base


def formatear_contexto(documentos):
    partes = []
    for numero, doc in enumerate(documentos, 1):
        fuente = doc.metadata.get("source", "Desconocida")
        partes.append(f"[{numero}] Fuente: {fuente}\n{doc.page_content}")
    return "\n\n".join(partes)


def calcular_costo(tokens):
    if not tokens:
        return None
    entrada = tokens.get("input_tokens")
    salida = tokens.get("output_tokens")
    if entrada is None or salida is None:
        return None
    precio_entrada = tarifa("PRECIO_ENTRADA_MILLON_USD", PRECIO_ENTRADA_MILLON_USD)
    precio_salida = tarifa("PRECIO_SALIDA_MILLON_USD", PRECIO_SALIDA_MILLON_USD)
    costo = (entrada * precio_entrada + salida * precio_salida) / 1_000_000
    return round(costo, 10)


def texto_respuesta(contenido):
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        textos = []
        for bloque in contenido:
            if isinstance(bloque, str):
                textos.append(bloque)
            elif isinstance(bloque, dict) and bloque.get("type") == "text":
                textos.append(str(bloque.get("text", "")))
        return "\n".join(textos).strip()
    return str(contenido)


def registrar_consulta(pregunta, vectorstore, modelo, k=3):
    print("\nPregunta:", pregunta)
    print("k =", k)
    inicio_total = time.perf_counter()
    inicio = time.perf_counter()
    documentos = vectorstore.similarity_search(pregunta, k=k)
    tiempo_busqueda = round((time.perf_counter() - inicio) * 1000, 2)
    if not documentos:
        raise RuntimeError("La base vectorial no devolvio documentos.")
    contexto = formatear_contexto(documentos)
    prompt = f"""Responde usando SOLO el contexto.
Cita las fuentes como [1], [2], etc.
Si no encuentras la respuesta, dilo.

CONTEXTO:
{contexto}

PREGUNTA:
{pregunta}

RESPUESTA:
"""
    inicio = time.perf_counter()
    respuesta = modelo.invoke(prompt)
    tiempo_generacion = round((time.perf_counter() - inicio) * 1000, 2)
    uso = getattr(respuesta, "usage_metadata", None)
    tokens = dict(uso) if uso else None
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pregunta": pregunta,
        "k": k,
        "chunks_recuperados": len(documentos),
        "modelo": MODELO_CHAT,
        "tiempos_ms": {"embed_y_busqueda": tiempo_busqueda, "generacion": tiempo_generacion},
        "tiempo_total_ms": round((time.perf_counter() - inicio_total) * 1000, 2),
        "tokens": tokens,
        "costo_generacion_usd": calcular_costo(tokens),
        "respuesta": texto_respuesta(respuesta.content),
    }
    with REGISTROS.open("a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
    print("\n========== RESULTADO ==========")
    print(json.dumps(registro, indent=2, ensure_ascii=False))
    return registro


def ejecutar_actividad():
    print("\n================================")
    print(" BLOQUE 28 - LATENCIA Y COSTO RAG")
    print("================================")
    configurar()
    embeddings = GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDING)
    vectorstore = preparar_vectorstore(embeddings)
    modelo = ChatGoogleGenerativeAI(model=MODELO_CHAT, temperature=0)
    preguntas = [
        "¿Que hace el cliente si ocurre un TimeoutError?",
        "¿Como funciona el sistema de reintentos?",
        "¿Como se registra el consumo de tokens?",
    ]
    for numero, pregunta in enumerate(preguntas, 1):
        print(f"\n========== CONSULTA {numero} ==========")
        registrar_consulta(pregunta, vectorstore, modelo, k=3)
    print("\n========== COMPARACION ==========")
    comparacion = []
    for k in (3, 6):
        comparacion.append(registrar_consulta(preguntas[0], vectorstore, modelo, k=k))
    print("\n========== RESUMEN ==========")
    for registro in comparacion:
        tokens = registro["tokens"] or {}
        print(f"k={registro['k']} | chunks={registro['chunks_recuperados']} | input_tokens={tokens.get('input_tokens')} | latencia={registro['tiempo_total_ms']} ms | costo_estimado_usd={registro['costo_generacion_usd']}")
    print("\nACTIVIDAD FINALIZADA")
    print("Archivo guardado:", REGISTROS)


if __name__ == "__main__":
    try:
        ejecutar_actividad()
    except Exception as error:
        print("\nERROR:", type(error).__name__)
        print(error)
        raise
