import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import joblib

from Python.src.config import ARQUIVO_CSV, ordem_sensores, MODELO_PATH

# -------------------------
# Carregamento do dataset
# -------------------------
# Lê o arquivo CSV com as amostras consideradas normais.
# Esse arquivo é a base usada para o treinamento do modelo.
df = pd.read_csv(ARQUIVO_CSV)

# Ordem das colunas usada no treinamento
# Deve ser a mesma ordem usada depois na inferência
colunas = ordem_sensores

# -------------------------
# Validação das colunas do CSV
# -------------------------
# Garante que o arquivo contém todas as colunas esperadas.
# Se faltar alguma, o treino é interrompido.
faltando = set(colunas) - set(df.columns)
if faltando:
    raise ValueError(f"CSV sem colunas esperadas: {sorted(faltando)}")

# -------------------------
# Limpeza e preparação dos dados
# -------------------------
# Converte os valores para numérico.
# Leituras inválidas (ex: 'NA') viram NaN e são removidas.
df[colunas] = df[colunas].apply(pd.to_numeric, errors="coerce")
df = df.dropna(subset=colunas)

# Matriz final usada no treinamento
X = df[colunas].values

# -------------------------
# Normalização
# -------------------------
# Padroniza os dados para média 0 e desvio padrão 1.
# O mesmo scaler será reutilizado durante a execução do sistema.
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -------------------------
# Treinamento do modelo de anomalia
# -------------------------
# O IsolationForest é treinado apenas com dados normais.
# Ele aprende o padrão esperado e marca desvios como anomalia.
model = IsolationForest(
    n_estimators=300,
    contamination=0.01,
    random_state=42
)
model.fit(X_scaled)

# -------------------------
# Salvamento do modelo
# -------------------------
# Salva o scaler e o modelo juntos para garantir consistência
# entre treinamento e inferência.
joblib.dump(
    {
        "scaler": scaler,
        "model": model,
        "colunas": colunas
    },
    MODELO_PATH
)

print(f"Modelo salvo em: {MODELO_PATH}")
