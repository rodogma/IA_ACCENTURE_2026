# Decisión de personalización para el caso propio

## Caso

Asistente académico que responde consultas sobre maquinaria, construcción y agentes usando el corpus del proyecto, con referencias para comprobar de dónde proviene cada dato.

Escala de 1 a 5; puntaje ponderado = suma de peso x puntaje, normalizado sobre 5.

| Criterio | Peso | RAG | Fine-tuning | PEFT |
|---|---:|---:|---:|---:|
| Información debe actualizarse al cambiar documentos | 30% | 5 | 2 | 2 |
| Respuestas deben citar fuentes | 25% | 5 | 1 | 1 |
| Ejemplos etiquetados suficientes para entrenar | 15% | 4 | 1 | 2 |
| Costo y facilidad de mantenimiento | 15% | 4 | 2 | 3 |
| Adaptación de estilo y formato | 15% | 3 | 4 | 4 |
| **Total ponderado / 5** | **100%** | **4.35** | **1.85** | **2.15** |

## Decisión

Se elige RAG porque la necesidad central es responder sobre el corpus actual y permitir verificar las afirmaciones mediante fuentes. Una actualización del corpus puede indexarse sin reentrenar el modelo. Fine-tuning o PEFT podrían ser complementos futuros para uniformar el estilo si se reúne un conjunto suficiente de respuestas aprobadas; no sustituyen las fuentes actualizables ni la citación.
