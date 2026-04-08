import os
import csv
import time
import random
from psychopy import visual, core, event, gui

# --- 1. CONSTANTES DEL PAPER CLÍNICO ---
TIEMPO_ESTIMULO = 1.0  # 1 segundo la letra
TIEMPO_ISI = 1.0       # 1 segundo la cruz
TIEMPO_PRE_BLOQUE = 10.0 # 10s antes del bloque real
TIEMPO_POST_BLOQUE = 20.0 # 20s al terminar el bloque real

UMBRALES_PRACTICA = {0: 0.80, 2: 0.80, 3: 0.70} # 80%, 80%, 70%
CARPETA_DATOS = "datos_pacientes"

# --- 2. GENERADOR DE SECUENCIAS (TARGETS Y LURES) ---
def generar_secuencia(nivel_n, total_letras):
    abecedario = ['A', 'B', 'C', 'D', 'E', 'F', 'H', 'J', 'M', 'N', 'P', 'R', 'T']
    
    # 0-BACK: El target es la 'X'. No hay Lures complejos.
    if nivel_n == 0:
        num_targets = int(total_letras * 0.20)
        secuencia = [random.choice(abecedario) for _ in range(total_letras)]
        indices = random.sample(range(total_letras), num_targets)
        for i in indices: secuencia[i] = 'X'
        return secuencia

    # N-BACK (>0): Generador con Targets (20%) y Lures (15%)
    num_targets = int(total_letras * 0.20)
    num_lures = int(total_letras * 0.15)
    
    secuencia = [None] * total_letras
    posiciones_validas = list(range(nivel_n, total_letras))
    
    # 1. Colocar Targets
    indices_targets = random.sample(posiciones_validas, num_targets)
    for i in indices_targets:
        if secuencia[i - nivel_n] is None:
            letra = random.choice(abecedario)
            secuencia[i] = letra
            secuencia[i - nivel_n] = letra
        else:
            secuencia[i] = secuencia[i - nivel_n]

    # 2. Colocar Lures (Trampas n-1 o n+1)
    posiciones_libres = [i for i in posiciones_validas if i not in indices_targets]
    indices_lures = random.sample(posiciones_libres, num_lures) if num_lures <= len(posiciones_libres) else posiciones_libres
    
    for i in indices_lures:
        desplazamiento = random.choice([-1, 1])
        indice_lure = i - nivel_n + desplazamiento
        if 0 <= indice_lure < total_letras:
            if secuencia[indice_lure] is None:
                letra = random.choice(abecedario)
                secuencia[indice_lure] = letra
                secuencia[i] = letra
            else:
                secuencia[i] = secuencia[indice_lure]

    # 3. Rellenar vacíos asegurando no crear targets accidentales
    for i in range(total_letras):
        if secuencia[i] is None:
            letra_prohibida = secuencia[i - nivel_n] if i >= nivel_n else None
            letras_validas = [l for l in abecedario if l != letra_prohibida]
            secuencia[i] = random.choice(letras_validas)
            
    return secuencia

# --- 3. FUNCIONES DE INTERFAZ ---
def mostrar_mensaje(texto, esperar_espacio=True):
    pantalla = visual.TextStim(win, text=texto, color='white', height=0.04, wrapWidth=1.5)
    pantalla.draw()
    win.flip()
    if esperar_espacio:
        event.waitKeys(keyList=['space'])

def mostrar_fijacion(tiempo):
    cruz.draw()
    win.flip()
    core.wait(tiempo)

def jugar_bloque(nivel_n, secuencia, es_practica=False):
    datos_bloque = []
    aciertos = 0
    ensayos_evaluados = 0
    
    for i, letra in enumerate(secuencia):
        es_target = False
        if nivel_n == 0:
            if letra == 'X': es_target = True
        else:
            if i >= nivel_n and letra == secuencia[i - nivel_n]: es_target = True

        # Fijación (1.0s estricto)
        cruz.draw()
        win.flip()
        core.wait(TIEMPO_ISI)
        
        # Letra (1.0s estricto)
        estimulo_letra.text = letra
        event.clearEvents(eventType='keyboard')
        reloj_rt.reset()
        estimulo_letra.draw()
        win.flip()
        core.wait(TIEMPO_ESTIMULO)
        
        # Captura de respuesta (durante la fijación siguiente, pero lo procesamos aquí para lógica)
        win.flip()
        tecla_presionada = False
        tiempo_reaccion = 0.0
        tecla = None
        
        # Esperamos respuesta (el paciente tiene el tiempo del estímulo + inicio del ISI para responder)
        teclas = event.getKeys(keyList=['k', 'l', 'escape'], timeStamped=reloj_rt)
        if teclas:
            tecla = teclas[0][0]
            tiempo_reaccion = teclas[0][1]
            if tecla == 'escape': 
                win.close()
                core.quit()

        # Evaluación
        if i < nivel_n and nivel_n != 0:
            categoria = "Ensayo Inicial"
        else:
            ensayos_evaluados += 1
            categoria = "Omision"
            if es_target:
                if tecla == 'k': 
                    categoria = "Hit"
                    aciertos += 1
                elif tecla == 'l': categoria = "Miss"
            else:
                if tecla == 'l': 
                    categoria = "Correct Rejection"
                    aciertos += 1
                elif tecla == 'k': categoria = "False Alarm"

        # Feedback Práctica Neutral
        if es_practica and categoria != "Ensayo Inicial":
            texto_fb = "Bien" if categoria in ["Hit", "Correct Rejection"] else "Error"
            visual.TextStim(win, text=texto_fb, color='white', height=0.06).draw()
            win.flip()
            core.wait(0.3) 

        datos_bloque.append({
            'Nivel': f"{nivel_n}-back", 'Ensayo': i + 1, 'Letra': letra, 
            'Es_Target': es_target, 'Tecla': tecla if tecla else "Ninguna",
            'Tiempo_Reaccion_seg': round(tiempo_reaccion, 3), 'Evaluacion': categoria
        })
        
    precision = (aciertos / ensayos_evaluados) if ensayos_evaluados > 0 else 0
    return datos_bloque, precision

# --- 4. INICIO Y DATOS ---
info_paciente = {'DNI': ''}
dlg = gui.DlgFromDict(dictionary=info_paciente, title='NeuroLab - Paradigma Clínico N-Back')
if not dlg.OK: core.quit()

dni = info_paciente['DNI']
if not dni.isdigit() or len(dni) < 8: core.quit()

os.makedirs(CARPETA_DATOS, exist_ok=True) 
archivo_csv = os.path.join(CARPETA_DATOS, f"datos_{dni}_{time.strftime('%Y%m%d_%H%M')}.csv")

win = visual.Window(size=(800, 600), fullscr=True, color='black', units='height')
cruz = visual.TextStim(win, text='+', color='white', height=0.1)
estimulo_letra = visual.TextStim(win, text='', color='white', height=0.2)
reloj_rt = core.Clock()

resultados_finales = []

# --- 5. BUCLE PRINCIPAL (PRÁCTICA Y EXPERIMENTO) ---
niveles = [0, 2, 3]

for nivel in niveles:
    mostrar_mensaje(f"--- FASE DE PRÁCTICA: {nivel}-BACK ---\n\n"
                    f"Necesitas {UMBRALES_PRACTICA[nivel]*100}% de precisión para pasar.\n"
                    f"{'Busca la X' if nivel == 0 else f'Compara con {nivel} letras atrás'}.\n\n"
                    f"K = SÍ, L = NO.\nPresiona ESPACIO para intentar.")
    
    paso_practica = False
    
    # Sistema Eliminatorio: 2 intentos máximo
    for intento in range(2):
        secuencia_practica = generar_secuencia(nivel, 10)
        _, precision = jugar_bloque(nivel, secuencia_practica, es_practica=True)
        
        if precision >= UMBRALES_PRACTICA[nivel]:
            paso_practica = True
            mostrar_mensaje(f"¡Práctica superada! Precisión: {precision*100}%\nPrepárate para la prueba real.")
            break
        else:
            if intento == 0:
                mostrar_mensaje(f"Precisión insuficiente ({precision*100}%). Necesitas {UMBRALES_PRACTICA[nivel]*100}%.\n"
                                f"Tienes UNA oportunidad más. Concéntrate.\nPresiona ESPACIO.")
            else:
                mostrar_mensaje(f"Precisión insuficiente ({precision*100}%).\n"
                                f"Lamentablemente no cumples el criterio para el experimento.\n"
                                f"Gracias por participar. El programa se cerrará.")
                core.quit() # Fin por eliminación
    
    if paso_practica:
        mostrar_mensaje(f"--- EXPERIMENTO REAL: {nivel}-BACK ---\n\n"
                        f"Iniciando en 10 segundos. Mantén la vista en la cruz.", esperar_espacio=False)
        mostrar_fijacion(TIEMPO_PRE_BLOQUE)
        
        secuencia_real = generar_secuencia(nivel, 20)
        datos_reales, _ = jugar_bloque(nivel, secuencia_real, es_practica=False)
        resultados_finales.extend(datos_reales)
        
        mostrar_mensaje("Bloque terminado. Descanso de 20 segundos.", esperar_espacio=False)
        mostrar_fijacion(TIEMPO_POST_BLOQUE)

# --- 6. EXPORTACIÓN DE DATOS ---
win.close()
with open(archivo_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['Nivel','Ensayo','Letra','Es_Target','Tecla','Tiempo_Reaccion_seg','Evaluacion'])
    writer.writeheader()
    writer.writerows(resultados_finales)
core.quit()