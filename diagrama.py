import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

# Cargar el archivo
archivo = "especies_disperso.xlsx"
df = pd.read_excel(archivo)

# Tomar los nombres de las columnas que representan años
columnas_años = df.columns[1:]  # primera columna es el nombre de la especie
años = pd.to_numeric(columnas_años, errors='coerce').dropna().astype(int).values.reshape(-1, 1)

# Crear la figura
plt.figure(figsize=(12, 7))

# Colores para distinguir líneas
colores = plt.cm.viridis(np.linspace(0, 1, len(df)))

# Graficar cada especie con puntos y su línea de regresión
for i in range(len(df)):
    especie = df.iloc[i, 0]
    poblacion = df.iloc[i, 1:].values.astype(float)
    
    # Asegurarse de no usar valores vacíos
    mask = ~np.isnan(poblacion)
    x = años[mask]
    y = poblacion[mask]
    
    if len(x) < 2:
        continue  # Se necesita al menos 2 puntos para ajustar línea
    
    modelo = LinearRegression()
    modelo.fit(x, y)
    y_pred = modelo.predict(x)

    # Graficar puntos
    plt.scatter(x, y, alpha=0.3, label=especie)

    # Graficar línea de regresión
    plt.plot(x, y_pred, color=colores[i], linewidth=2)

    # Calcular año en que se extingue (población = 0)
    if modelo.coef_[0] != 0:
        año_extincion = -modelo.intercept_ / modelo.coef_[0]
        if x.min() <= año_extincion <= x.max():
            plt.axvline(x=año_extincion, color=colores[i], linestyle='--', alpha=0.3)

# Mostrar gráfico
plt.title("Tendencia de extinción por especie")
plt.xlabel("Años antes de extinción (0 = extinta)")
plt.ylabel("Población estimada")
plt.grid(True)
plt.tight_layout()
plt.show()
