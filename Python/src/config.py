# -------------------------
# Configurações do modelo
# -------------------------
# Usadas tanto no treinamento quanto na execução.

ordem_sensores = ["MQ7", "MQ2", "T", "U"]
MODELO_PATH = "../models/modelo_anomalia.joblib"

# -------------------------
# Protocolo Serial (mensagens do Arduino)
# -------------------------
campos_obrigatorios = ["ID=", "MQ7=", "MQ2=", "T=", "U=", "S="]
campos_filtrados = ["MQ7", "MQ2", "T", "U"]
# -------------------------
# Arquivos
# -------------------------
ARQUIVO_CSV = "../data/dados_normais.csv"

# -------------------------
# Comunicação Serial
# -------------------------
PORTA_ARDUINO = "COM5"
BAUDRATE = 9600
TIMEOUT_SERIAL_S = 2

# -------------------------
# Parâmetros de processamento
# -------------------------
TAMANHO_MEDIA_MOVEL = 10
JANELA_PREDICAO = 5
