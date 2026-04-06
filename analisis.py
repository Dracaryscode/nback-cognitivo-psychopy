import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

# 1. Buscar el archivo CSV más reciente en la carpeta
archivos_csv = glob.glob("datos_paciente_*.csv")
ultimo_archivo = max(archivos_csv, key=os.path.getctime)

print(f"Analizando los datos de: {ultimo_archivo}")

# 2. Cargar los datos con Pandas
df = pd.read_csv(ultimo_archivo)

# Configurar el estilo visual (Estilo científico/limpio)
sns.set_theme(style="whitegrid")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))

# --- GRÁFICO 1: Precisión (Conteo de Evaluaciones) ---
# Contamos cuántos Hits, Misses, etc. hubo
conteo_evaluacion = df['Evaluacion'].value_counts()

sns.barplot(x=conteo_evaluacion.index, y=conteo_evaluacion.values, ax=ax1, palette="viridis")
ax1.set_title("Precisión del Paciente: Distribución de Respuestas", fontsize=14, fontweight='bold')
ax1.set_ylabel("Cantidad de Ensayos")
ax1.set_xlabel("")

# --- GRÁFICO 2: Tiempos de Reacción (Solo donde presionó el botón) ---
# Filtramos solo los ensayos donde el RT es mayor a 0
df_rt = df[df['Tiempo_Reaccion_seg'] > 0]

sns.boxplot(x='Evaluacion', y='Tiempo_Reaccion_seg', data=df_rt, ax=ax2, palette="mako")
sns.stripplot(x='Evaluacion', y='Tiempo_Reaccion_seg', data=df_rt, ax=ax2, color='black', alpha=0.5, size=8)

ax2.set_title("Velocidad: Tiempos de Reacción por Tipo de Respuesta", fontsize=14, fontweight='bold')
ax2.set_ylabel("Tiempo de Reacción (Segundos)")
ax2.set_xlabel("")

# Ajustar diseño y mostrar
plt.tight_layout()
plt.show()