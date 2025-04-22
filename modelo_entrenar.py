import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

df = pd.read_csv("data/especies_extintas.csv")
df_t = df.set_index("Año").T
df_t = df_t.dropna()

X = df_t.values
y = np.array([0] * len(df_t))

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

model = Sequential([
    Dense(64, activation="relu", input_shape=(X.shape[1],)),
    Dense(32, activation="relu"),
    Dense(1)
])

model.compile(optimizer="adam", loss="mse")
model.fit(X_train, y_train, epochs=100, verbose=1)

model.save("modelo_entrenado.h5")
joblib.dump(scaler, "scaler.save")