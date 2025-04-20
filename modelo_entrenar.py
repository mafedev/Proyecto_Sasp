# modelo.py (ENTRENAMIENTO DEL MODELO - solo se ejecuta una vez para generar el .h5)
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 1. Cargar CSV
df = pd.read_csv("data/especies_extintas.csv")

# 2. Poner especies como filas y años como columnas
df_t = df.set_index('Año').T
df_t = df_t.dropna()  # Quitar las que tengan datos faltantes

# 3. X son los datos de población histórica, y es siempre 0 (porque ya están extintas)
X = df_t.values
y = np.array([0] * len(df_t))  # Todas se extinguieron

# 4. Normalizar los datos
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 5. Dividir para entrenar
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# 6. Crear la red neuronal
model = Sequential([
    Dense(64, activation='relu', input_shape=(X.shape[1],)),
    Dense(32, activation='relu'),
    Dense(1)
])

# 7. Compilar y entrenar
model.compile(optimizer='adam', loss='mse')
model.fit(X_train, y_train, epochs=100, verbose=1)

# 8. Guardar el modelo
model.save("modelo_entrenado.h5")