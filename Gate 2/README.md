# Gate 2: servicio RAG modular

Entrega integrada para el corpus del proyecto sobre maquinaria, construcción y agentes. El servicio reutiliza el índice Chroma persistido en `Modulo_2/bloque_24/vectorstore`, colección `corpus_bloque_24`.

## Requisitos

- Python 3.10 o superior.
- Acceso al repositorio completo: esta carpeta usa el índice y el corpus de `Modulo_2/bloque_24`.
- Clave Gemini guardada localmente en `.env` como `GEMINI_API_KEY`.
- Dependencias del proyecto instaladas en un entorno virtual.

Nunca agregues `.env`, claves ni el entorno virtual al commit.

## Instalación limpia en Windows

Abre PowerShell en la raíz `IA_ACCENTURE_2026` y ejecuta:

```powershell
python --version
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Configura `.env` en la raíz con `GEMINI_API_KEY`. Para estimar costo, añade las tarifas vigentes del modelo usado, expresadas en USD por millón de tokens:

```dotenv
PRECIO_ENTRADA_MILLON_USD=0.30
PRECIO_SALIDA_MILLON_USD=2.50
```

Confirma que los paquetes principales estén instalados:

```powershell
python -m pip show chromadb langchain-chroma langchain-core langchain-google-genai langgraph python-dotenv
```

El entorno `IA_Accenture.venv` existente también funciona; la instalación limpia anterior es una comprobación reproducible, no reemplaza automáticamente ese entorno.

## Índice y consulta

Comprueba que `Modulo_2/bloque_24/vectorstore` exista y contenga el índice antes de consultar. Para indexar o actualizar incrementalmente el corpus con los identificadores estables del indexador del proyecto:

```powershell
python ".\Gate 2\servicio_rag.py" --indexar
```

Ejecuta una consulta real de punta a punta:

```powershell
python ".\Gate 2\servicio_rag.py" --pregunta "¿Qué maquinaria recomienda el corpus para nivelar un terreno?"
```

La consulta real recupera el primer resultado por defecto (`RAG_K=1`), filtra documentos con patrones de inyección, genera respuesta con Gemini, añade referencias verificables, registra tokens/costo/latencia y guarda evidencia. Cambia `RAG_K` si quieres experimentar con otro número de fragmentos.

## Evaluación y controles

```powershell
python ".\Gate 2\servicio_rag.py" --evaluar
python ".\Gate 2\servicio_rag.py" --verificar-filtro
python ".\Gate 2\servicio_rag.py" --supervisar
python -m pytest test_gate2.py -v
```

`--evaluar` consulta el índice persistido con cinco preguntas del corpus y reporta precision, recall y F1 en `@1` y `@3`. Cada pregunta tiene una fuente relevante etiquetada; el JSON indica esta definición. `--verificar-filtro` comprueba una cadena normal y una instrucción de inyección sin llamar a Gemini. `--supervisar` pausa el grafo LangGraph con `interrupt()` y espera la decisión humana para reanudar con `Command(resume=...)`. Las pruebas automáticas usan un store/LLM simulados para no consumir API; la consulta real se conserva como evidencia aparte.

## Archivos de evidencia

- `resultados_metricas.json`: evaluación del retrieval sobre el índice del corpus.
- `evidencias_corridas.jsonl`: corrida real o simulada, pregunta, respuesta, fuentes, tokens, costo y latencia. Trátalo como evidencia con contenido; revisa y anonimiza antes de compartirlo.
- `trazas.jsonl`: logging estructurado con `trace_id`, etapas, conteos, tokens y tiempos. No guarda texto crudo de pregunta, documentos ni respuesta.
- `registro_prompts.jsonl`: hashes de la versión base de referencia y de la versión activa, sin almacenar contenido de consulta.
- `supervision_humana.jsonl`: huella del prompt, decisión y thread_id de la supervisión real.
- `matriz_riesgos.md`: riesgos específicos del caso y controles humanos.
- `decision_personalizacion.md`: puntuación comparativa RAG, fine-tuning y PEFT para este caso.
- `autoevaluacion_gate2.md`: autoevaluación ponderada y checklist final.

## Cierre de entrega

Desde la raíz, revisa el estado del repositorio y confirma que `.env` no vaya incluido:

```powershell
git status --short
git diff --check
```

Añade solo los archivos de entrega y pruebas que correspondan, crea el commit solicitado por el curso y verifica `git status --short` y `git log -1 --oneline` antes de entregar.
