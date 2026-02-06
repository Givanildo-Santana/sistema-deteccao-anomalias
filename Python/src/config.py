# -------------------------
# Configurações do modelo
# -------------------------
# Informações usadas tanto no treinamento quanto na execução do modelo.
# Qualquer mudança aqui afeta diretamente o pipeline de ML.

# Ordem dos sensores exatamente como o modelo foi treinado.
# Essa ordem DEVE ser respeitada na hora de montar o vetor de entrada.
ordem_sensores = ["MQ7", "MQ2", "T", "U"]

# Caminho do arquivo do modelo treinado (scaler + modelo salvos via joblib)
MODELO_PATH = "../models/modelo_anomalia.joblib"


# -------------------------
# Configurações do protocolo Serial
# -------------------------
# Definem o formato esperado das mensagens recebidas do Arduino.

# Campos que DEVEM existir em toda mensagem "LEITURA|..."
# Usado para validar se a leitura está completa antes de processar.
campos_obrigatorios = ["ID=", "MQ7=", "MQ2=", "T=", "U=", "S="]

# Campos que serão extraídos da mensagem e usados no processamento.
# Esses valores entram no cálculo da média móvel e no modelo.
campos_filtrados = ["MQ7", "MQ2", "T", "U"]


# -------------------------
# Arquivos
# -------------------------
# Caminhos de arquivos usados pelo sistema.

# CSV usado para armazenar amostras consideradas normais
# (base para o treinamento do modelo de anomalia)
ARQUIVO_CSV = "dados_normais.csv"


# -------------------------
# Comunicação
# -------------------------
# Parâmetros da comunicação Serial com o Arduino.

# Porta onde o Arduino está conectado e velocidade da comunicação
PORTA_ARDUINO = "COM5"
BAUDRATE = 9600


# -------------------------
# Parâmetros de processamento
# -------------------------
# Ajustes que controlam o comportamento do algoritmo em tempo de execução.

# Quantidade de leituras usadas no cálculo da média móvel
TAMANHO_MEDIA_MOVEL = 10

# Quantidade de predições usadas para decidir se há anomalia
# (ex: 5 predições seguidas anormais → alerta)
JANELA_PREDICAO = 5
