import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# 1. Cargar CSV de especies extintas
df = pd.read_csv("data/especies_extintas.csv")

# 2. Reorganizar: especies como filas, años como columnas
df_t = df.set_index("Año").T
df_t = df_t.dropna()  # Eliminar especies con datos faltantes

# 3. Calcular pendiente de los últimos 10 años para cada especie
def calcular_pendiente_ultimos_anios(fila, n=10):
    ultimos = fila[-n:]  # Últimos n valores
    x = np.arange(len(ultimos))
    y = ultimos.values
    x_mean, y_mean = np.mean(x), np.mean(y)
    pendiente = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
    return pendiente

df_t["pendiente_reciente"] = df_t.apply(calcular_pendiente_ultimos_anios, axis=1)

# 4. Separar X (entradas) e y (etiquetas)
X = df_t.values
y = np.array([0] * len(df_t))  # Todas están extintas

# 5. Escalar los datos
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 6. Dividir en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# 7. Crear red neuronal con activación sigmoid para salida entre 0 y 1
model = Sequential([
    Dense(64, activation="relu", input_shape=(X.shape[1],)),
    Dense(32, activation="relu"),
    Dense(1, activation="sigmoid")  # Salida probabilística
])

# 8. Compilar con función de pérdida para clasificación binaria
model.compile(optimizer="adam", loss="binary_crossentropy")

# 9. Entrenar el modelo
model.fit(X_train, y_train, epochs=100, verbose=1)

# 10. Guardar el modelo y el scaler
model.save("modelo_entrenado.h5")
joblib.dump(scaler, "scaler.save")

print("Modelo y scaler guardados correctamente.")