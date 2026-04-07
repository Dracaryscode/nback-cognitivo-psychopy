import csv
import time
import random
from psychopy import visual, core, event, gui

# --- 1. CONSTANTES DEL EXPERIMENTO ---
N_BACK = 2
TIEMPO_FIJACION_MIN = 0.4  # 400 ms
TIEMPO_FIJACION_MAX = 0.6  # 600 ms
TIEMPO_ESTIMULO = 0.5  
TIEMPO_ISI = 1.0       

# --- 2. FUNCIONES DEL MOTOR (LÓGICA) ---
def generar_bloque_nback(n_back, total_letras, prob_target=0.3):
    """Fábrica de secuencias pseudo-aleatorias"""
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
    """Muestra un texto en pantalla y espera a que el paciente presione ESPACIO"""
    pantalla = visual.TextStim(win, text=texto, color='white', height=0.04, wrapWidth=1.5)
    pantalla.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

def jugar_bloque(secuencia, guardar_datos=True):
    """Ejecuta la secuencia de letras en pantalla. Solo devuelve datos si guardar_datos es True"""
    datos_bloque = []
    
    for i, letra in enumerate(secuencia):
        es_target = False
        if i >= N_BACK:
            if letra == secuencia[i - N_BACK]:
                es_target = True

        # 1. Fijación con Jittering (Tiempo aleatorio)
        jitter = random.uniform(TIEMPO_FIJACION_MIN, TIEMPO_FIJACION_MAX)
        cruz.draw()
        win.flip()
        core.wait(jitter)
        
        # Preparar
        estimulo_letra.text = letra
        event.clearEvents(eventType='keyboard')
        reloj_rt.reset()
        
        # 2. Estímulo
        estimulo_letra.draw()
        win.flip()
        core.wait(TIEMPO_ESTIMULO)
        
        # 3. ISI (Pantalla Negra)
        win.flip()
        
        tecla_presionada = False
        tiempo_reaccion = 0.0
        tiempo_inicio_isi = core.getTime()
        
        while core.getTime() - tiempo_inicio_isi < TIEMPO_ISI:
            teclas = event.getKeys(keyList=['space', 'escape'], timeStamped=reloj_rt)
            if teclas and not tecla_presionada: 
                tecla = teclas[0][0]
                tiempo_reaccion = teclas[0][1]
                tecla_presionada = True
                if tecla == 'escape': 
                    win.close()
                    core.quit()

        # Evaluación y Guardado
        if guardar_datos:
            categoria = ""
            if es_target and tecla_presionada: categoria = "Hit (Acierto)"
            elif es_target and not tecla_presionada: categoria = "Miss (Omision)"
            elif not es_target and tecla_presionada: categoria = "False Alarm (Falsa Alarma)"
            elif not es_target and not tecla_presionada: categoria = "Correct Rejection (Rechazo Correcto)"

            datos_bloque.append({
                'Ensayo': i + 1,
                'Letra': letra,
                'Es_Target': es_target,
                'Presiono_Boton': tecla_presionada,
                'Tiempo_Reaccion_seg': round(tiempo_reaccion, 3),
                'Evaluacion': categoria
            })
            
    return datos_bloque

# --- 3. INICIO DEL PROGRAMA Y DATOS DEL PACIENTE ---
info_paciente = {'DNI': ''}

# 1. PRIMERO abramos la ventana para pedir el dato
dlg = gui.DlgFromDict(dictionary=info_paciente, title='Datos del Paciente - NeuroLab')

# Si presiona Cancelar, salimos
if not dlg.OK: 
    core.quit()

# 2. LUEGO extraemos lo que escribió y lo validamos
dni_paciente = info_paciente['DNI']

if not dni_paciente.isdigit() or len(dni_paciente) < 8:
    print("Error: DNI inválido. El programa se cerrará.")
    core.quit()

nombre_archivo = f"datos_{dni_paciente}_{time.strftime('%Y%m%d_%H%M')}.csv"
# --- 4. PREPARACIÓN GRÁFICA ---
win = visual.Window(size=(800, 600), fullscr=True, color='black', units='height')
cruz = visual.TextStim(win, text='+', color='white', height=0.1)
estimulo_letra = visual.TextStim(win, text='', color='white', height=0.2)
reloj_rt = core.Clock()

# --- 5. BLOQUE DE PRÁCTICA ---
texto_practica = """Vamos a hacer una PRÁCTICA de 10 letras.
Recuerda: Presiona la BARRA ESPACIADORA cuando la letra sea igual a la de hace DOS turnos.
Estos datos NO serán evaluados.

(Presiona ESPACIO para iniciar la práctica)"""

mostrar_mensaje(texto_practica)
secuencia_practica = generar_bloque_nback(N_BACK, total_letras=10, prob_target=0.3)
# Llamamos a jugar_bloque pero con guardar_datos=False
jugar_bloque(secuencia_practica, guardar_datos=False) 

# --- 6. BLOQUE EXPERIMENTAL (REAL) ---
texto_real = """¡Práctica terminada! 
Ahora comenzará el EXPERIMENTO REAL de 30 letras.
Concéntrate al máximo.

(Presiona ESPACIO para iniciar la prueba)"""

mostrar_mensaje(texto_real)
secuencia_real = generar_bloque_nback(N_BACK, total_letras=30, prob_target=0.3)
# Aquí SÍ guardamos los datos
resultados_finales = jugar_bloque(secuencia_real, guardar_datos=True)

# --- 7. CIERRE Y EXPORTACIÓN ---
win.close()

with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo_csv:
    campos = ['Ensayo', 'Letra', 'Es_Target', 'Presiono_Boton', 'Tiempo_Reaccion_seg', 'Evaluacion']
    escritor = csv.DictWriter(archivo_csv, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(resultados_finales)

print(f"\n¡Experimento finalizado! Datos del paciente {info_paciente['DNI']} guardados en: {nombre_archivo}")

# AGREGA ESTA LÍNEA AL FINAL PARA EVITAR EL CRASHEO EN MAC
core.quit()