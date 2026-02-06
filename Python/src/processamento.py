# -------------------------
# Cálculo da média móvel
# -------------------------
# Atualiza o histórico de cada sensor e calcula a média móvel.
# A média só é calculada quando o buffer atinge o tamanho esperado.
def calcular_media_movel(dados_tratados, buffer_sensores, media_leituras):

    # Percorre cada sensor presente na leitura atual
    for sensor in dados_tratados:

        # Cria o buffer do sensor caso seja a primeira leitura
        if sensor not in buffer_sensores:
            buffer_sensores[sensor] = []

        # Adiciona o valor atual ao histórico
        buffer_sensores[sensor].append(dados_tratados[sensor])

        # Mantém o buffer com tamanho fixo (descarta o mais antigo)
        if len(buffer_sensores[sensor]) > 10:
            buffer_sensores[sensor].pop(0)

        # Calcula a média apenas quando o buffer está completo
        if len(buffer_sensores[sensor]) == 10:
            media_leituras[sensor] = round(
                sum(buffer_sensores[sensor]) / 10, 2
            )

    return media_leituras


# -------------------------
# Montagem do vetor de entrada
# -------------------------
# Organiza as médias móveis no formato esperado pelo modelo,
# respeitando a ordem definida no treinamento.
def vetor(media_leituras, vetor_base, ordem_sensores):

    # Limpa o vetor antes de montar uma nova entrada
    vetor_base.clear()

    # Garante que todas as médias necessárias estão disponíveis
    for sensor in ordem_sensores:
        if sensor not in media_leituras:
            return None

        vetor_base.append(media_leituras[sensor])

    return vetor_base
