import os
import csv
import time
import random
from psychopy import visual, core, event, gui

# --- 1. CONSTANTES DEL EXPERIMENTO ---
N_BACK = 2
TIEMPO_FIJACION_MIN = 0.4  
TIEMPO_FIJACION_MAX = 0.6  
TIEMPO_ESTIMULO = 0.5  
TIEMPO_ISI = 1.0       
CARPETA_DATOS = "datos_pacientes"

# --- 2. FUNCIONES DEL MOTOR ---
def generar_bloque_nback(n_back, total_letras, prob_target=0.3):
    abecedario = ['A', 'B', 'C', 'D', 'E', 'F', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'R', 'T']
    num_targets = int(total_letras * prob_target) 
    posiciones_validas = list(range(n_back, total_letras))
    turnos_targets = random.sample(posiciones_validas, num_targets)
    
    secuencia = []
    for i in range(total_letras):
        if i in turnos_targets:
            secuencia.append(secuencia[i - n_back])
        else:
            letra_prohibida = secuencia[i - n_back] if i >= n_back else None
            letra_anterior = secuencia[i - 1] if i >= 1 else None
            letras_validas = [l for l in abecedario if l not in (letra_prohibida, letra_anterior)]
            secuencia.append(random.choice(letras_validas))
    return secuencia

def mostrar_mensaje(texto):
    pantalla = visual.TextStim(win, text=texto, color='white', height=0.04, wrapWidth=1.5)
    pantalla.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

def jugar_bloque(secuencia, guardar_datos=True, es_practica=False):
    datos_bloque = []
    
    for i, letra in enumerate(secuencia):
        es_target = False
        if i >= N_BACK:
            if letra == secuencia[i - N_BACK]:
                es_target = True

        # 1. Fijación con Jittering
        jitter = random.uniform(TIEMPO_FIJACION_MIN, TIEMPO_FIJACION_MAX)
        cruz.draw()
        win.flip()
        core.wait(jitter)
        
        # Preparar estímulo
        estimulo_letra.text = letra
        event.clearEvents(eventType='keyboard')
        reloj_rt.reset()
        
        # 2. Mostrar Letra
        estimulo_letra.draw()
        win.flip()
        core.wait(TIEMPO_ESTIMULO)
        
        # 3. ISI (Pantalla Negra y Captura)
        win.flip()
        
        tecla_presionada = False
        tiempo_reaccion = 0.0
        tecla = None
        tiempo_inicio_isi = core.getTime()
        
        while core.getTime() - tiempo_inicio_isi < TIEMPO_ISI:
            teclas = event.getKeys(keyList=['k', 'l', 'escape'], timeStamped=reloj_rt)
            if teclas and not tecla_presionada: 
                tecla = teclas[0][0]
                tiempo_reaccion = teclas[0][1]
                tecla_presionada = True
                if tecla == 'escape': 
                    win.close()
                    core.quit()

        # Evaluación lógica
        if i < N_BACK:
            categoria = "Ensayo Inicial"
        else:
            categoria = "Omision"
            if es_target:
                if tecla == 'k': categoria = "Hit (Acierto)"
                elif tecla == 'l': categoria = "Miss (Error)"
            else:
                if tecla == 'l': categoria = "Correct Rejection"
                elif tecla == 'k': categoria = "False Alarm"

        # Feedback de Práctica (Neutral y sin avisos de lentitud)
        if es_practica and i >= N_BACK and tecla_presionada:
            texto_fb = "Correcto" if "Correct" in categoria or "Hit" in categoria else "Incorrecto"
            # Color blanco para evitar sesgos de ansiedad
            feedback = visual.TextStim(win, text=texto_fb, color='white', height=0.06)
            feedback.draw()
            win.flip()
            core.wait(0.3) 

        if guardar_datos:
            datos_bloque.append({
                'Ensayo': i + 1, 'Letra': letra, 'Es_Target': es_target,
                'Tecla': tecla if tecla else "Ninguna",
                'Tiempo_Reaccion_seg': round(tiempo_reaccion, 3),
                'Evaluacion': categoria
            })
    return datos_bloque

# --- 3. INICIO ---
info_paciente = {'DNI': ''}
dlg = gui.DlgFromDict(dictionary=info_paciente, title='NeuroLab - N-Back')
if not dlg.OK: core.quit()

dni_paciente = info_paciente['DNI']
if not dni_paciente.isdigit() or len(dni_paciente) < 8: core.quit()

os.makedirs(CARPETA_DATOS, exist_ok=True) 
nombre_archivo = os.path.join(CARPETA_DATOS, f"datos_{dni_paciente}_{time.strftime('%Y%m%d_%H%M')}.csv")

# --- 4. VENTANA ---
win = visual.Window(size=(800, 600), fullscr=True, color='black', units='height')
cruz = visual.TextStim(win, text='+', color='white', height=0.1)
estimulo_letra = visual.TextStim(win, text='', color='white', height=0.2)
reloj_rt = core.Clock()

# --- 5. BLOQUES ---
mostrar_mensaje("""Vamos a hacer una PRÁCTICA de 10 letras.

IMPORTANTE: Las primeras DOS letras son solo para observar y memorizar.
A partir de la TERCERA letra, debes empezar a responder:

- Presiona 'K' (SÍ) si la letra es IGUAL a la de hace DOS turnos.
- Presiona 'L' (NO) si es DIFERENTE.

(Presiona ESPACIO para iniciar la práctica)""")

jugar_bloque(generar_bloque_nback(N_BACK, 10), guardar_datos=False, es_practica=True)

mostrar_mensaje("""¡Práctica terminada! 

Ahora comenzará el EXPERIMENTO REAL de 30 letras.
Recuerda: Memoriza las dos primeras, y a partir de la tercera responde:
'K' para SÍ, 'L' para NO.

Ya NO verás mensajes de correcto/incorrecto. Concéntrate.

(Presiona ESPACIO para iniciar la prueba)""")
res = jugar_bloque(generar_bloque_nback(N_BACK, 30), guardar_datos=True)

# --- 6. CIERRE ---
win.close()
with open(nombre_archivo, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['Ensayo','Letra','Es_Target','Tecla','Tiempo_Reaccion_seg','Evaluacion'])
    writer.writeheader()
    writer.writerows(res)
core.quit()