import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Cargar el archivo
archivo = "especies_disperso.xlsx"
df = pd.read_excel(archivo)

# Tomar los nombres de las columnas que representan años
columnas_años = df.columns[1:]  # primera columna es el nombre de la especie
años = pd.to_numeric(columnas_años, errors='coerce').dropna().astype(int)

# Crear la figura
plt.figure(figsize=(10, 6))

# Graficar todas las especies con puntos
for i in range(len(df)):
    especie = df.iloc[i, 0]
    valores = df.iloc[i, 1:].values
    plt.scatter(años, valores, alpha=0.3)

# 📌 Calcular la media de población por año (eje y)
poblaciones_promedio = df.iloc[:, 1:].mean(axis=0).values

# 📌 Ajuste lineal: np.polyfit(x, y, grado)
pendiente, intercepto = np.polyfit(años, poblaciones_promedio, 1)

# 📌 Crear línea ajustada
linea_ajustada = pendiente * años + intercepto

# Dibujar la línea de ajuste general
plt.plot(años, linea_ajustada, color='red', linestyle='--', linewidth=2, label=f"Tendencia general\nPendiente: {pendiente:.2f}")

# Mostrar info
plt.xlabel("Tiempo (años)")
plt.ylabel("Población estimada")
plt.title("Tendencia general de la población de especies extintas")
plt.xticks(rotation=45)
plt.legend(loc="upper right")
plt.grid(True)
plt.show()
