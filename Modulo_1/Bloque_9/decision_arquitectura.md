# Decisión de arquitectura: elección de modelo

**Proyecto:** IA_ACCENTURE_2026  
**Fecha de evaluación:** 22-10-2026

## Modelo elegido

**Candidato inicial:** Gemini 3.5 Flash-Lite (`gemini-3.5-flash-lite`).

Se utiliza para responder preguntas de texto mediante la API de Google Gemini. La elección definitiva se fundamentará en la comparación de latencia, costo y calidad frente al segundo modelo.

## Diagrama de arquitectura

![Diagrama de arquitectura Gemini](./Arquitectura_miniaplicacion_Gemini.png)

La miniaplicación utiliza `main.py` y el módulo `consumir_api_3.py`, compuesto por `armar_peticion()`, `enviar_peticion()` y `extraer_texto()`.

La credencial `GEMINI_API_KEY` se obtiene desde el archivo `.env`. El consumo de tokens se consulta en `usageMetadata` para calcular el costo estimado.

## Comparación de candidatos

| Criterio | Gemini 3.5 Flash-Lite | Gemini 3.6 Flash |
|---|---|---|
| Costo por 1.000 tokens de entrada | USD 0,00030 | USD 0,00075 |
| Costo por 1.000 tokens de salida | USD 0,00250 | USD 0,00375 |
| Latencia promedio observada | Pendiente de medición | Pendiente de medición |
| Calidad para preguntas simples | Pendiente de evaluación | Pendiente de evaluación |

**Fuente de precios:** https://ai.google.dev/gemini-api/docs/pricing

## Justificación

Gemini 3.5 Flash-Lite es el candidato inicial porque la miniaplicación está orientada a consultas sencillas de texto y su tarifa es inferior a la de Gemini 3.6 Flash.

Se confirmará esta elección cuando se comparen los tiempos promedio observados y la calidad de las respuestas generadas en condiciones equivalentes.

## Alternativa descartada y por qué
Se descarta Gemini 3.5 Flash-Lite como modelo principal de la miniaplicación, debido a su mayor tiempo de respuesta en las pruebas realizadas.

En cuatro consultas idénticas, Gemini 3.5 Flash-Lite registró una latencia promedio de 12,06 segundos, mientras que Gemini 3.6 Flash obtuvo 2,51 segundos, siendo aproximadamente 4,8 veces más rápido.

Aunque Gemini 3.5 Flash-Lite presentó un menor costo de operación, ambos modelos respondieron correctamente las consultas efectuadas. Por lo tanto, para esta miniaplicación se prioriza la rapidez de respuesta y la experiencia del usuario por sobre el ahorro económico.

En consecuencia, se selecciona Gemini 3.6 Flash, considerando que su mayor costo estimado resulta aceptable para el volumen reducido de consultas del proyecto.

**Alternativa Ganadora:** Gemini 3.6 Flash.


