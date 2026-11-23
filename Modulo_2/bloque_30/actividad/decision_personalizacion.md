# Decision de personalizacion

## 1. El problema
El asistente de maquinaria de construccion necesita responder preguntas tecnicas utilizando informacion documental verificable y mantener sus respuestas alineadas con las fuentes disponibles.

### Evidencia y criterios

- **informacion_cambia_seguido: False**. Pendiente: revisar fechas de modificacion de las fuentes durante los ultimos 3 meses.
- **problema_de_formato_o_tono: False**. Pendiente: revisar 20 respuestas y contar cuantos incumplimientos de formato o tono existen.
- **dataset_grande_y_de_calidad: False**. El proyecto tiene 9 casos de evaluacion de recuperacion, pero no consta un dataset de 200 ejemplos etiquetados para entrenamiento.
- **presupuesto_limitado_o_iterar_rapido: True**. Supuesto por confirmar: se prioriza iterar rapidamente sin financiar multiples entrenamientos.
- **necesita_multiples_variantes: False**. Actualmente se trabaja con un unico asistente RAG; no se ha definido una necesidad de varias versiones.

## 2. Resultado del metodo de decision

- RAG: 2 puntos
- PEFT: 1 puntos
- Fine-tuning completo: 0 puntos

**Tecnica mejor puntuada: RAG**

## 3. Tecnica elegida y por que

Se propone RAG porque el proyecto ya dispone de un sistema de recuperacion semantica basado en embeddings y Chroma. Esta estrategia permite incorporar documentos al corpus sin entrenar nuevamente los parametros del modelo.

## 4. Que necesitarias para ejecutarla

El proyecto ya cuenta con 5 documentos indexados en Chroma y 9 casos de evaluacion de recuperacion. Para ampliar el sistema se deben identificar nuevas fuentes de maquinaria, cimentacion y procedimientos tecnicos, verificar su calidad y agregarlas al indice vectorial.

**Pendiente:** definir y contar exactamente cuantos documentos adicionales se necesitan antes de entregar la actividad.

**Nota:** verificar las respuestas y evidencias antes de considerar definitiva esta decision.