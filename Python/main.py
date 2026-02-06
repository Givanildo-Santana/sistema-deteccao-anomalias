import joblib

from Python.src.arduino_serial import con_arduino, controle_arduino
from Python.src.parser_serial import conversao_dados
from Python.src.processamento import calcular_media_movel, vetor
from Python.src.modelo_ml import padronizar_dados, predicao, alerta
from Python.src.config import (
    ordem_sensores,
    campos_obrigatorios,
    campos_filtrados,
    PORTA_ARDUINO,
    MODELO_PATH
)

# -------------------------
# Carregamento do modelo
# -------------------------
# Carrega o modelo de anomalia e o scaler treinados previamente.
# Esses objetos são usados durante toda a execução do sistema.
bundle = joblib.load(MODELO_PATH)
scaler = bundle["scaler"]
model = bundle["model"]

# -------------------------
# Buffers e estados do sistema
# -------------------------
# Estruturas usadas para acumular leituras e controlar o fluxo:
# - buffer_sensores: histórico bruto de cada sensor
# - media_leituras: médias móveis calculadas
# - vetor_base: vetor final usado como entrada do modelo
# - vetor_predicoes: histórico recente das predições
buffer_sensores = {}
media_leituras = {}
vetor_base = []
vetor_predicoes = []

# -------------------------
# Conexão com o Arduino
# -------------------------
# Abre a comunicação serial com o Arduino usando a porta configurada.
conexao_arduino = con_arduino(PORTA_ARDUINO)

contador = 1

# -------------------------
# Loop principal
# -------------------------
# Executa continuamente:
# 1) solicita leitura ao Arduino
# 2) valida e converte os dados recebidos
# 3) calcula médias móveis
# 4) executa a predição de anomalia
# 5) envia comando de alerta ou normal ao Arduino
while True:

    # Solicita uma nova leitura ao Arduino
    dados_brutos = controle_arduino(b'#01\n', conexao_arduino)

    # Converte e valida a mensagem recebida
    dados_tratado = conversao_dados(
        dados_brutos,
        campos_obrigatorios,
        campos_filtrados
    )

    # Ignora a leitura se estiver incompleta ou inválida
    if dados_tratado is None:
        continue

    # Atualiza buffers e calcula a média móvel dos sensores
    calcular_media_movel(
        dados_tratado,
        buffer_sensores,
        media_leituras
    )

    # Só prossegue quando já existem médias calculadas
    if media_leituras:
        # Monta o vetor de entrada respeitando a ordem do modelo
        vetor(
            media_leituras,
            vetor_base,
            ordem_sensores
        )

        # Normaliza os dados e executa a predição
        vetor_scaled = padronizar_dados(vetor_base, scaler)
        predicao(vetor_scaled, model, vetor_predicoes)

        # Decide se o estado atual é normal ou anômalo
        status_alerta = alerta(vetor_predicoes)

        # Envia comando correspondente ao Arduino
        if status_alerta is True:
            conexao_arduino.write(b'#03\n')
            print("*********** !!! ALERTA !!! *********** ")
        else:
            conexao_arduino.write(b'#02\n')
            print("*********** NORMAL *********** ")

    print(contador)
    contador += 1
