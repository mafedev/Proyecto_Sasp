import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

df = pd.read_csv("data/especies_extintas.csv") # Cargar CSV de especies extintas


df_t = df.set_index("Año").T # Utiliza la columna año como índice
df_t = df_t.dropna()  # Eliminar especies con datos faltantes

# Calcular pendiente de los últimos 10 años para cada especie
def calcular_pendiente_ultimos_anios(fila, n=10):
    ultimos = fila[-n:]  # Últimos 10 años
    x = np.arange(len(ultimos))
    y = ultimos.values
    prom_x, prom_y = np.mean(x), np.mean(y)
    pendiente = np.sum((x - prom_x) * (y - prom_y)) / np.sum((x - prom_x) ** 2)
    return pendiente

df_t["pendiente_reciente"] = df_t.apply(calcular_pendiente_ultimos_anios, axis=1)

# Entradas y etiquetas
X = df_t.values # Matriz
y = np.array([0] * len(df_t)) # Todas están extintas

scaler = StandardScaler() # Normaliza los datos
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42) # Divide los datos en 80% entrenamiento y 20% prueba

# Red neuronal
model = Sequential([
    Dense(64, activation="relu", input_shape=(X.shape[1],)), # Primera capa
    Dense(32, activation="relu"),
    Dense(1, activation="sigmoid")  # Salida entre 0 y 1
])

# Compilar con función de pérdida para clasificación binaria
model.compile(optimizer="adam", loss="binary_crossentropy")

# Se entrena el modelo
model.fit(X_train, y_train, epochs=100, verbose=1)

# Guarda el modelo y el scaler
model.save("modelo_entrenado.h5")
joblib.dump(scaler, "scaler.save")