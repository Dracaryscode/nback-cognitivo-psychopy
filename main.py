import csv
import time
from psychopy import visual, core, event, gui

# --- 1. CONFIGURACIÓN Y DATOS DEL PACIENTE ---
N_BACK = 2
LETRAS_PRUEBA = ['A', 'B', 'A', 'C', 'X', 'C', 'X', 'B'] 
TIEMPO_FIJACION = 0.5
TIEMPO_ESTIMULO = 0.5
TIEMPO_ISI = 1.0

# Cuadro de diálogo para ingresar el DNI
info_paciente = {'DNI': ''}
dlg = gui.DlgFromDict(dictionary=info_paciente, title='Datos del Paciente - NeuroLab')

# Si el usuario presiona "Cancelar" en el cuadro, el programa se cierra
if not dlg.OK:
    core.quit()

dni_paciente = info_paciente['DNI']
# El CSV ahora incluye el DNI
nombre_archivo = f"datos_{dni_paciente}_{time.strftime('%Y%m%d_%H%M')}.csv"

win = visual.Window(size=(800, 600), fullscr=False, color='black', units='height')
cruz = visual.TextStim(win, text='+', color='white', height=0.1)
estimulo_letra = visual.TextStim(win, text='', color='white', height=0.2)
reloj_rt = core.Clock()

# --- 2. PANTALLA DE CONSIGNA (INSTRUCCIONES) ---
texto_consigna = """Hola, gracias por participar. Este es un juego de memoria.

Aparecerán letras una por una en el centro de la pantalla.

Tu trabajo es presionar la BARRA ESPACIADORA ÚNICAMENTE cuando 
la letra que veas sea EXACTAMENTE IGUAL a la que viste DOS TURNOS ATRÁS.

Ejemplo: A -> B -> A (¡Aquí presionas el botón!)

Si te equivocas, no te preocupes, sigue concentrado en la siguiente.

Presiona la BARRA ESPACIADORA cuando estés listo para comenzar."""

instrucciones = visual.TextStim(win, text=texto_consigna, color='white', height=0.04, wrapWidth=1.5)
instrucciones.draw()
win.flip()

# El programa se pausa aquí infinitamente hasta que presione 'space'
event.waitKeys(keyList=['space']) 
# -----------------------------------------------

resultados = []

# --- 3. BUCLE DEL JUEGO ---
for i, letra in enumerate(LETRAS_PRUEBA):
    
    es_target = False
    if i >= N_BACK:
        if letra == LETRAS_PRUEBA[i - N_BACK]:
            es_target = True

    # 1. Fijación
    cruz.draw()
    win.flip()
    core.wait(TIEMPO_FIJACION)
    
    # Preparar el ensayo
    estimulo_letra.text = letra
    event.clearEvents(eventType='keyboard')
    reloj_rt.reset()
    
    # 2. Mostrar Estímulo
    estimulo_letra.draw()
    win.flip()
    core.wait(TIEMPO_ESTIMULO)
    
    # 3. Pantalla Negra (Intervalo / ISI)
    win.flip()
    
    tecla_presionada = False
    tiempo_reaccion = 0.0
    
    # Captura de teclado
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

    # Evaluación psicológica
    categoria = ""
    if es_target and tecla_presionada:
        categoria = "Hit (Acierto)"
    elif es_target and not tecla_presionada:
        categoria = "Miss (Omision)"
    elif not es_target and tecla_presionada:
        categoria = "False Alarm (Falsa Alarma)"
    elif not es_target and not tecla_presionada:
        categoria = "Correct Rejection (Rechazo Correcto)"

    resultados.append({
        'Ensayo': i + 1,
        'Letra': letra,
        'Es_Target': es_target,
        'Presiono_Boton': tecla_presionada,
        'Tiempo_Reaccion_seg': round(tiempo_reaccion, 3),
        'Evaluacion': categoria
    })

# --- 4. CIERRE Y EXPORTACIÓN A CSV ---
win.close()

with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo_csv:
    campos = ['Ensayo', 'Letra', 'Es_Target', 'Presiono_Boton', 'Tiempo_Reaccion_seg', 'Evaluacion']
    escritor = csv.DictWriter(archivo_csv, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(resultados)

print(f"\n¡Experimento finalizado con éxito! Datos guardados en: {nombre_archivo}")