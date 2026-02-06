# -------------------------
# Padronização dos dados
# -------------------------
# Aplica o mesmo scaler do treinamento para deixar os valores na escala correta.
# O modelo espera receber os dados já normalizados.
def padronizar_dados(vetor_entrada, scaler):
    # scaler.transform espera um "array 2D", por isso envolvemos em [ ... ]
    return scaler.transform([vetor_entrada])


# -------------------------
# Predição + histórico recente
# -------------------------
# Faz a predição do modelo e guarda o resultado em um buffer (vetor_saida).
# O buffer serve para tomar decisão com base em várias predições seguidas,
# e não em uma única leitura (evita falso alarme).
def predicao(vetor_padronizado, modelo_treinado, vetor_saida):
    # IsolationForest retorna -1 (anomalia) ou 1 (normal)
    pred = int(modelo_treinado.predict(vetor_padronizado)[0])

    # Mantém somente as últimas 5 predições no buffer
    if len(vetor_saida) >= 5:
        vetor_saida.pop(0)

    vetor_saida.append(pred)
    return pred


# -------------------------
# Decisão de alerta
# -------------------------
# Decide se entra em modo alerta olhando o buffer de predições.
# Só começa a decidir quando já tem 5 resultados acumulados.
def alerta(vetor_predicoes):
    if len(vetor_predicoes) < 5:
        return "Dados Insuficientes"

    # Conta quantas vezes apareceu -1 (anomalia)
    anomalia = sum(1 for p in vetor_predicoes if p == -1)

    # Se deu anomalia em todas as 5 últimas, ativa alerta
    return anomalia >= 5
