# IA_ACCENTURE_2026

## Descripción del proyecto

Proyecto desarrollado durante el programa de formación en Inteligencia Artificial Generativa de Accenture, utilizando Python y la API de Google Gemini.

El repositorio reúne los ejercicios prácticos desarrollados durante los diferentes bloques del curso, aplicando conceptos de programación modular, consumo de APIs, gestión segura de credenciales, manejo de errores, ingeniería de prompts y análisis del rendimiento de modelos generativos.

## Objetivo

Desarrollar una miniaplicación en Python capaz de enviar preguntas a un modelo de inteligencia artificial generativa, procesar sus respuestas y presentar los resultados al usuario.

Además, el proyecto incorpora herramientas para realizar pruebas de consistencia de prompts, validar respuestas JSON y analizar el comportamiento de los modelos utilizados.

## Tecnologías utilizadas

- Python
- Google Gemini API
- Requests
- Python-dotenv
- JSON
- Git y GitHub
- Visual Studio Code

## Estructura del proyecto

```text
IA_ACCENTURE_2026/
│
├── docs/                    # Documentación del proyecto
├── IA_Accenture.venv/       # Entorno virtual local
│
├── Modulo_1/
│   ├── Bloque_1/
│   ├── Bloque_2/
│   ├── Bloque_3/
│   ├── Bloque_4/
│   ├── Bloque_5/
│   ├── Bloque_6/
│   ├── Bloque_7/
│   ├── Bloque_8/
│   ├── Bloque_9/
│   ├── Bloque_10/
│   │   └── consumir_api_6.py
│   │
│   └── prompts/
│       ├── banco_prompts.py
│       └── modulo1/
│           ├── cliente_gemini.py
│           └── probar_consistencia.py
│
├── src/
│   ├── Consumir_api.py
│   └── main.py
│
├── test/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Funcionamiento de la miniaplicación

La aplicación permite al usuario enviar preguntas a Google Gemini y recibir respuestas generadas mediante inteligencia artificial.

El funcionamiento general consta de las siguientes etapas:

1. El usuario escribe una pregunta desde la terminal.
2. `main.py` recibe la pregunta.
3. `Consumir_api.py` obtiene la clave `GEMINI_API_KEY` desde el archivo `.env`.
4. La aplicación construye una petición HTTP POST a Google Gemini.
5. Gemini procesa la solicitud y devuelve una respuesta en formato JSON.
6. Python extrae el contenido generado.
7. `main.py` muestra la respuesta al usuario y gestiona los posibles errores.

### Arquitectura

```text
Usuario
   |
   v
main.py
   |
   | Pregunta
   v
Consumir_api.py
   |
   | Credencial desde .env
   | Petición HTTP POST
   v
Google Gemini API
   |
   | Respuesta JSON
   v
Consumir_api.py
   |
   | Texto generado
   v
main.py
   |
   v
Respuesta al usuario
```

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/rodogma/IA_ACCENTURE_2026.git
cd IA_ACCENTURE_2026
```

### 2. Crear un entorno virtual

```powershell
python -m venv IA_Accenture.venv
```

### 3. Activar el entorno virtual en Windows

```powershell
.\IA_Accenture.venv\Scripts\Activate.ps1
```

### 4. Instalar dependencias

```powershell
python -m pip install -r requirements.txt
```

### 5. Configurar la clave de Gemini

Crear un archivo `.env` en la raíz del proyecto:

```dotenv
GEMINI_API_KEY=TU_CLAVE_API
```

La credencial debe mantenerse privada. El archivo `.env` y el entorno virtual deben estar excluidos del control de versiones mediante `.gitignore`.

## Ejecutar la miniaplicación

Desde la raíz del proyecto:

```powershell
python .\src\main.py
```

La terminal solicitará una pregunta:

```text
Escribe tu pregunta para Gemini:
```

Ejemplo:

```text
Tu pregunta: ¿Qué es Python?

Respuesta de Gemini:
Python es un lenguaje de programación de alto nivel...
```

La aplicación permite realizar consultas a Gemini y recibir las respuestas directamente en la terminal.

## Banco de prompts

El proyecto incorpora un banco de prompts reutilizables para evaluar distintas tareas de procesamiento de lenguaje natural.

Se incluyen tres categorías principales:

**Clasificación de sentimientos:** analiza textos y devuelve un sentimiento junto con un nivel de confianza.

**Extracción de entidades:** identifica lugares mencionados en un texto y los devuelve en una estructura JSON.

**Resumen de textos:** genera resúmenes breves utilizando instrucciones de sistema.

Los prompts se encuentran definidos en:

`Modulo_1/prompts/banco_prompts.py`

## Validación de consistencia

El archivo `probar_consistencia.py` realiza pruebas automáticas utilizando la API de Gemini.

Cada prompt se ejecuta tres veces para comprobar que el modelo genere respuestas JSON válidas y con la estructura esperada.

El proceso valida:

- La sintaxis JSON de la respuesta.
- La presencia de claves obligatorias.
- Los tipos de datos esperados.
- Las restricciones específicas de cada prompt.
- El porcentaje de respuestas válidas.

### Ejecutar pruebas

```powershell
python .\Modulo_1\prompts\modulo1\probar_consistencia.py
```

### Registro de resultados

El script genera automáticamente el archivo:

`Modulo_1/prompts/registro_resultados.json`

El registro contiene el total de intentos, respuestas válidas, fallos, porcentajes de consistencia y detalles de las respuestas evaluadas.

## Manejo de errores

La miniaplicación incorpora controles para detectar errores habituales:

- Credencial API no configurada.
- Preguntas vacías o con tipos de datos incorrectos.
- Fallos de conexión.
- Solicitudes que superan el tiempo de espera.
- Respuestas HTTP con errores.
- Respuestas JSON inválidas o incompletas.

Las excepciones se utilizan para identificar problemas y presentar mensajes comprensibles al usuario.

## Comparación de modelos

Durante el desarrollo se realizaron pruebas de rendimiento para comparar:

- Gemini 3.5 Flash-Lite
- Gemini 3.6 Flash

En cuatro consultas idénticas por modelo se obtuvieron los siguientes resultados:

| Criterio | Gemini 3.5 Flash-Lite | Gemini 3.6 Flash |
|---|---:|---:|
| Pruebas exitosas | 4/4 | 4/4 |
| Latencia promedio | 12,06 segundos | 2,51 segundos |
| Costo total estimado de las pruebas | USD 0,00018710 | USD 0,00170775 |

En estas pruebas, Gemini 3.6 Flash presentó una menor latencia, mientras que Gemini 3.5 Flash-Lite mostró un menor costo estimado.

Estos resultados corresponden a pruebas puntuales y pueden variar según las condiciones de conexión, la disponibilidad del servicio y las características de cada consulta.

## Seguridad

El proyecto utiliza variables de entorno para evitar incorporar directamente la credencial de Gemini en el código fuente.

Se recomienda no publicar archivos `.env`, claves API, información sensible ni carpetas de entornos virtuales en el repositorio.

## Estado del proyecto

**En desarrollo.**

El proyecto continuará incorporando nuevos ejercicios, mejoras en la arquitectura y funcionalidades relacionadas con inteligencia artificial generativa a medida que avance el programa de formación.

---

**Proyecto académico — IA_ACCENTURE_2026**  
Python · Google Gemini API · Inteligencia Artificial Generativa
