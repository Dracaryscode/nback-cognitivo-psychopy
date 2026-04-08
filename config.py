# config.py

# --- TIEMPOS Y UMBRALES (Ocultos al paciente) ---
TIEMPO_ESTIMULO = 1.0  
TIEMPO_ISI = 1.0       
TIEMPO_PRE_BLOQUE = 10.0 
TIEMPO_POST_BLOQUE = 20.0 

UMBRALES_PRACTICA = {0: 0.80, 2: 0.80, 3: 0.70}
CARPETA_DATOS = "datos_pacientes"

# --- TEXTOS EXPLICATIVOS PARA EL PACIENTE ---
TEXTO_BIENVENIDA = """Bienvenido al experimento de Memoria de Trabajo del NeuroLab.

En esta prueba evaluaremos tu capacidad de concentración y memoria.
A lo largo de la sesión, verás diferentes letras aparecer en el centro de la pantalla.

Tu tarea será presionar los botones 'K' (SÍ) o 'L' (NO) dependiendo de las instrucciones de cada fase.

Por favor, ubica tus dedos en las teclas K y L.
(Presiona ESPACIO para continuar)"""

TEXTOS_INSTRUCCIONES = {
    0: """--- TAREA 0-BACK (Atención Básica) ---

En esta fase, solo debes buscar una letra en específico.

- Presiona 'K' (SÍ) cada vez que veas la letra 'X'.
- Presiona 'L' (NO) para cualquier otra letra.

Primero haremos una práctica. El sistema te dirá si aciertas o fallas.
(Presiona ESPACIO para iniciar la práctica)""",
    
    2: """--- TAREA 2-BACK (Memoria de Trabajo) ---

Ahora la tarea requiere memoria.
Debes recordar la letra que apareció hace exactamente DOS turnos.

- Presiona 'K' (SÍ) si la letra actual es IGUAL a la de hace dos turnos.
- Presiona 'L' (NO) si es DIFERENTE.

(Ejemplo: A -> B -> A. En la segunda 'A' presionas SÍ)
Primero practicaremos.
(Presiona ESPACIO para iniciar)""",
    
    3: """--- TAREA 3-BACK (Alta Exigencia) ---

Esta es la fase de mayor concentración.
Ahora debes comparar la letra actual con la que apareció hace TRES turnos.

- Presiona 'K' (SÍ) si la letra es IGUAL a la de hace tres turnos.
- Presiona 'L' (NO) si es DIFERENTE.

Haremos una última práctica. 
(Presiona ESPACIO para iniciar)"""
}