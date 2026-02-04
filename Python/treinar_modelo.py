import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import joblib

ARQUIVO = "dados_normais.csv"

# 1) Carrega dataset
df = pd.read_csv(ARQUIVO)

# Garante a ordem esperada (igual ao seu header)
colunas = ["MQ7", "MQ2", "T", "U"]
X = df[colunas].astype(float).values

# 2) Normaliza (muito importante pra ML)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 3) Modelo de anomalia (treina só com normal)
# contamination = quanto você "aceita" que possa ser anomalia no treino (use baixo)
model = IsolationForest(
    n_estimators=300,
    contamination=0.01,   # 1% (ajuste depois)
    random_state=42
)
model.fit(X_scaled)

# 4) Salva scaler + modelo
joblib.dump({"scaler": scaler, "model": model, "colunas": colunas}, "modelo_anomalia.joblib")
print("Modelo salvo em: modelo_anomalia.joblib")
