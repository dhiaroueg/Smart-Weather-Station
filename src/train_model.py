# train_model.py
import numpy as np
import pandas as pd
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split

CSV = "thingspeak_data.csv"
N_STEPS = 6      # fenêtre (6 lectures * 30s ou 10s selon ton envoi)
HORIZON = 3      # prédire T + HORIZON steps
EPOCHS = 60
BATCH = 32

# Charger et nettoyer
df = pd.read_csv(CSV, parse_dates=["created_at"])
df = df.sort_values("created_at").reset_index(drop=True)
# garder seulement temperature pour commencer
df['temp'] = pd.to_numeric(df['temp'], errors='coerce')
df['temp'] = df['temp'].interpolate().ffill().bfill()

values = df['temp'].values.astype(np.float32)

# construction X, y
X, y = [], []
for i in range(len(values) - N_STEPS - HORIZON + 1):
    X.append(values[i:i+N_STEPS])
    y.append(values[i+N_STEPS+HORIZON-1])
X = np.array(X)  # shape (samples, N_STEPS)
y = np.array(y)  # shape (samples,)

# scale simple (mean/std)
mean = X.mean()
std  = X.std()
Xs = (X - mean) / std
ys = (y - mean) / std

X_train, X_test, y_train, y_test = train_test_split(Xs, ys, test_size=0.2, shuffle=False)

# Model simple fully-connected
model = keras.Sequential([
    layers.Input(shape=(N_STEPS,)),
    layers.Dense(64, activation='relu'),
    layers.Dense(32, activation='relu'),
    layers.Dense(1)
])
model.compile(optimizer='adam', loss='mse', metrics=['mae'])

history = model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH,
                    validation_data=(X_test, y_test))

# eval
loss, mae = model.evaluate(X_test, y_test)
print("Test MAE (normalized):", mae)

# save model + scaler params
model.save("model_keras.h5")
np.savez("scaler_params.npz", mean=mean, std=std, N_STEPS=N_STEPS, HORIZON=HORIZON)
print("Saved model_keras.h5 and scaler_params.npz")
