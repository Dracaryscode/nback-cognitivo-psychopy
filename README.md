# N-Back Cognitive Task (PsychoPy)

Este proyecto implementa la clásica tarea experimental **N-Back** utilizada en neurociencia y psicología para medir la memoria de trabajo y el control de interferencias. 

Desarrollado para la automatización de toma de datos experimentales, capturando tiempos de reacción (RT) con precisión de milisegundos y evaluando respuestas (Hits, Misses, False Alarms, Correct Rejections).

## Estructura del Proyecto
- `main.py`: Motor gráfico del experimento. Despliega la consigna, renderiza los estímulos y exporta un log en `.csv`.
- `analisis.py`: Script de Pandas y Seaborn que lee el `.csv` generado y crea un dashboard visual automático (Precisión y Velocidad).

## Tecnologías
* Python 3.9
* PsychoPy (Estimulación y captura de hardware)
* Pandas & Seaborn (Análisis de datos y visualización)