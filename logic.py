# logic.py
import random

def generar_secuencia(nivel_n, total_letras):
    """Genera secuencias con Targets (20%) y Lures n-1/n+1 (15%)"""
    abecedario = ['A', 'B', 'C', 'D', 'E', 'F', 'H', 'J', 'M', 'N', 'P', 'R', 'T']
    
    if nivel_n == 0:
        num_targets = int(total_letras * 0.20)
        secuencia = [random.choice(abecedario) for _ in range(total_letras)]
        indices = random.sample(range(total_letras), num_targets)
        for i in indices: secuencia[i] = 'X'
        return secuencia

    num_targets = int(total_letras * 0.20)
    num_lures = int(total_letras * 0.15)
    
    secuencia = [None] * total_letras
    posiciones_validas = list(range(nivel_n, total_letras))
    
    # 1. Targets
    indices_targets = random.sample(posiciones_validas, num_targets)
    for i in indices_targets:
        if secuencia[i - nivel_n] is None:
            letra = random.choice(abecedario)
            secuencia[i] = letra
            secuencia[i - nivel_n] = letra
        else:
            secuencia[i] = secuencia[i - nivel_n]

    # 2. Lures (Trampas)
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

    # 3. Relleno
    for i in range(total_letras):
        if secuencia[i] is None:
            letra_prohibida = secuencia[i - nivel_n] if i >= nivel_n else None
            letras_validas = [l for l in abecedario if l != letra_prohibida]
            secuencia[i] = random.choice(letras_validas)
            
    return secuencia