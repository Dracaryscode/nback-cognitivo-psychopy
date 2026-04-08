# main.py
import os
import csv
import time
from psychopy import visual, core, event, gui
import config as cfg  # Importamos nuestras constantes y textos
import logic          # Importamos nuestro motor matemático

# --- 1. INGRESO DE DATOS ---
info_paciente = {'DNI': ''}
dlg = gui.DlgFromDict(dictionary=info_paciente, title='NeuroLab - Paradigma Clínico N-Back')
if not dlg.OK: core.quit()

dni = info_paciente['DNI']
if not dni.isdigit() or len(dni) < 8: core.quit()

os.makedirs(cfg.CARPETA_DATOS, exist_ok=True) 
archivo_csv = os.path.join(cfg.CARPETA_DATOS, f"datos_{dni}_{time.strftime('%Y%m%d_%H%M')}.csv")

# --- 2. CONFIGURACIÓN VISUAL ---
win = visual.Window(size=(800, 600), fullscr=True, color='black', units='height')
cruz = visual.TextStim(win, text='+', color='white', height=0.1)
estimulo_letra = visual.TextStim(win, text='', color='white', height=0.2)
reloj_rt = core.Clock()

def mostrar_mensaje(texto, esperar_espacio=True):
    visual.TextStim(win, text=texto, color='white', height=0.04, wrapWidth=1.5).draw()
    win.flip()
    if esperar_espacio: event.waitKeys(keyList=['space'])

def mostrar_fijacion(tiempo):
    cruz.draw()
    win.flip()
    core.wait(tiempo)

def jugar_bloque(nivel_n, secuencia, es_practica=False):
    datos_bloque = []
    aciertos = 0
    ensayos_evaluados = 0
    
    for i, letra in enumerate(secuencia):
        es_target = (nivel_n == 0 and letra == 'X') or (nivel_n > 0 and i >= nivel_n and letra == secuencia[i - nivel_n])

        cruz.draw()
        win.flip()
        core.wait(cfg.TIEMPO_ISI)
        
        estimulo_letra.text = letra
        event.clearEvents(eventType='keyboard')
        reloj_rt.reset()
        estimulo_letra.draw()
        win.flip()
        core.wait(cfg.TIEMPO_ESTIMULO)
        
        win.flip()
        teclas = event.getKeys(keyList=['k', 'l', 'escape'], timeStamped=reloj_rt)
        tecla, tiempo_reaccion = (teclas[0][0], teclas[0][1]) if teclas else (None, 0.0)
        if tecla == 'escape': core.quit()

        if i < nivel_n and nivel_n != 0:
            categoria = "Ensayo Inicial"
        else:
            ensayos_evaluados += 1
            if es_target:
                categoria = "Hit" if tecla == 'k' else "Miss"
                if tecla == 'k': aciertos += 1
            else:
                categoria = "Correct Rejection" if tecla == 'l' else "False Alarm"
                if tecla == 'l': aciertos += 1
            if not tecla: categoria = "Omision"

        # Feedback solo en práctica (Mantenido, pero sin porcentajes)
        if es_practica and categoria != "Ensayo Inicial":
            texto_fb = "Correcto" if categoria in ["Hit", "Correct Rejection"] else "Incorrecto"
            visual.TextStim(win, text=texto_fb, color='white', height=0.06).draw()
            win.flip()
            core.wait(0.3) 

        datos_bloque.append({
            'Nivel': f"{nivel_n}-back", 'Ensayo': i + 1, 'Letra': letra, 
            'Es_Target': es_target, 'Tecla': tecla if tecla else "Ninguna",
            'Tiempo_Reaccion_seg': round(tiempo_reaccion, 3), 'Evaluacion': categoria
        })
        
    return datos_bloque, (aciertos / ensayos_evaluados) if ensayos_evaluados > 0 else 0

# --- 3. BUCLE PRINCIPAL ---
resultados_finales = []
mostrar_mensaje(cfg.TEXTO_BIENVENIDA)

for nivel in [0, 2, 3]:
    mostrar_mensaje(cfg.TEXTOS_INSTRUCCIONES[nivel])
    paso_practica = False
    
    # Sistema Eliminatorio Silencioso (No muestra el porcentaje al usuario)
    for intento in range(2):
        secuencia_practica = logic.generar_secuencia(nivel, 10)
        _, precision = jugar_bloque(nivel, secuencia_practica, es_practica=True)
        
        if precision >= cfg.UMBRALES_PRACTICA[nivel]:
            paso_practica = True
            mostrar_mensaje("¡Práctica superada!\nYa estás listo para la fase real de este nivel.\n\nRecuerda: Ya no verás si la respuesta es correcta o incorrecta.\n\n(Presiona ESPACIO)")
            break
        else:
            if intento == 0:
                mostrar_mensaje("Parece que aún podemos mejorar antes de iniciar.\nVamos a intentar la práctica una vez más.\n\n(Presiona ESPACIO)")
            else:
                mostrar_mensaje("Gracias por tu esfuerzo.\nPor diseño del estudio, detendremos la prueba en esta fase.\n\n(Presiona ESPACIO para cerrar)")
                core.quit() 
    
    if paso_practica:
        mostrar_mensaje(f"Iniciando EXPERIMENTO REAL {nivel}-BACK en 10 segundos.\nMantén la vista en la cruz.", esperar_espacio=False)
        mostrar_fijacion(cfg.TIEMPO_PRE_BLOQUE)
        
        secuencia_real = logic.generar_secuencia(nivel, 20)
        datos_reales, _ = jugar_bloque(nivel, secuencia_real, es_practica=False)
        resultados_finales.extend(datos_reales)
        
        if nivel != 3:
            mostrar_mensaje("Bloque terminado.\nDescansa un momento, continuaremos en 20 segundos.", esperar_espacio=False)
            mostrar_fijacion(cfg.TIEMPO_POST_BLOQUE)

mostrar_mensaje("¡Experimento completado exitosamente!\nMuchas gracias por tu participación.\n\n(Presiona ESPACIO para salir)")

# --- 4. EXPORTACIÓN ---
win.close()
with open(archivo_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['Nivel','Ensayo','Letra','Es_Target','Tecla','Tiempo_Reaccion_seg','Evaluacion'])
    writer.writeheader()
    writer.writerows(resultados_finales)
core.quit() 