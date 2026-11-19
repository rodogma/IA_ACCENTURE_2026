# Límites de la métrica de evaluación

## Qué mide

El pipeline evalúa las respuestas generadas por Google Gemini comparándolas con una referencia mediante tres métricas: precisión, cobertura y F1.

La precisión mide qué proporción de las palabras de la respuesta aparece en la referencia. La cobertura mide qué proporción de las palabras de la referencia aparece en la respuesta. F1 combina ambas métricas.

Antes de calcularlas, el pipeline normaliza y tokeniza los textos.

Estas métricas permiten medir la coincidencia de palabras, pero no comprenden directamente el significado, la corrección factual ni la completitud de las respuestas.

## Modos de falla conocidos

Durante la revisión manual se identificaron los siguientes problemas:

- **Interpretación incorrecta del contexto:** en el caso 15, Gemini interpretó «biblioteca» como un lugar de préstamo de libros, cuando la referencia describía una biblioteca de programación. Su F1 fue 0.2308.

- **Ambigüedad de las preguntas:** en el caso 6, Gemini respondió sobre un diccionario de palabras en lugar de un diccionario de Python. Su F1 fue 0.2759. La respuesta era válida en otro contexto, pero no correspondía al concepto esperado.

- **Respuestas correctas con F1 bajo:** en el caso 7, Gemini explicó correctamente el funcionamiento de un bucle `for`, pero obtuvo un F1 de 0.2941 porque utilizó una explicación más extensa que la referencia.

- **Respuestas correctas pero incompletas:** en el caso 14, Gemini describió un módulo como una unidad reutilizable de código, pero no especificó que en Python un módulo es un archivo con código. Su F1 fue 0.2941.

- **Información adicional que reduce la coincidencia de palabras:** en el caso 2, Gemini explicó correctamente qué es una variable, pero obtuvo un F1 de 0.3077 porque su respuesta incluía más detalles que la referencia.

Estos resultados demuestran que un F1 bajo no siempre indica una respuesta incorrecta y que la métrica no permite identificar por sí sola todos los problemas de calidad.

## Muestra revisada

Se generaron 20 respuestas utilizando `consultar_modelo` y se calcularon sus métricas.

Se seleccionaron 10 respuestas para revisión manual: las cinco con F1 más bajo y las cinco con F1 más alto.

**Casos con F1 bajo:**

| Caso | Tema | F1 |
|---|---|---|
| 15 | Biblioteca | 0.2308 |
| 6 | Diccionario | 0.2759 |
| 7 | Bucle for | 0.2941 |
| 14 | Módulo | 0.2941 |
| 2 | Variable | 0.3077 |

**Casos con F1 alto:**

| Caso | Tema | F1 |
|---|---|---|
| 16 | Pip | 0.4667 |
| 4 | Lista en Python | 0.4706 |
| 19 | JSON | 0.4706 |
| 20 | Git | 0.5000 |
| 5 | Tupla | 0.5714 |

La revisión manual permitió identificar respuestas que no correspondían al contexto esperado y otras que eran correctas a pesar de obtener puntuaciones F1 bajas.

En los casos de mayor F1, las respuestas revisadas fueron correctas y completas, aunque ninguna alcanzó una coincidencia perfecta con su referencia.

## Recomendación de uso

Se recomienda utilizar F1 como una herramienta inicial para comparar respuestas y seleccionar casos que requieran revisión.

No se recomienda utilizar esta métrica como único criterio para determinar si una respuesta es correcta.

En este pipeline, la revisión manual es especialmente importante cuando:

- La pregunta puede interpretarse en distintos contextos.
- La respuesta utiliza sinónimos o explicaciones más extensas.
- La respuesta omite información importante de la referencia.
- Es necesario comprobar la veracidad del contenido.

También se recomienda redactar preguntas más específicas, por ejemplo, «¿Qué es un diccionario en Python?» en lugar de «¿Qué es un diccionario?».

**Conclusión:** la combinación de métricas automáticas y revisión manual ofrece una evaluación más útil que el F1 por sí solo. Los resultados del Bloque 17 demuestran que la coincidencia de palabras no equivale necesariamente a calidad de respuesta.