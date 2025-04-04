import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Cargar el archivo con años negativos
archivo = "especies_disperso.xlsx"  # Asegúrate de tener este archivo

# Determinar el formato y cargar los datos
if archivo.endswith(".xlsx"):
    df = pd.read_excel(archivo)
elif archivo.endswith(".csv"):
    df = pd.read_csv(archivo)

# 📌 Ver los nombres de las columnas antes de procesarlas
print("Columnas originales:", df.columns.tolist())

# 🔹 Limpiar y convertir los años correctamente (asegurar que sean enteros negativos)
columnas_años = df.columns[1:]  # Omitimos la primera columna porque es "Especies"
años = pd.to_numeric(columnas_años, errors='coerce').dropna().astype(int)

# 🔹 Ordenar los años en orden descendente (de -100 a 0)
# años = sorted(años, reverse=True)

# 🔹 Verificar si hubo conversiones incorrectas
print("Años convertidos correctamente:", años)

# Crear la figura
plt.figure(figsize=(10, 6))

# Graficar cada especie con puntos (sin líneas)
for i in range(len(df)):
    especie = df.iloc[i, 0]  # Nombre de la especie
    valores = df.iloc[i, 1:].values  # Poblaciones
    plt.scatter(años, valores, alpha=0.6, label=especie)  # 📌 Solo puntos

# Mejorar la visualización
plt.xlabel("Tiempo (años)")
plt.ylabel("Población estimada")
plt.title("Evolución de la población de especies extintas")
plt.xticks(rotation=45)
plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1))  # Ubicar la leyenda fuera del gráfico
plt.grid(True)

# Mostrar la gráfica
plt.show()