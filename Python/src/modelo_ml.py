from config import JANELA_PREDICAO

# -------------------------
# Padronização dos dados
# -------------------------
# Aplica o mesmo scaler do treinamento para deixar os valores na escala correta.
# O modelo espera receber os dados já normalizados.
def padronizar_vetor(vetor_entrada, scaler_modelo):
    # scaler.transform espera um "array 2D", por isso envolvemos em [ ... ]
    return scaler_modelo.transform([vetor_entrada])


# -------------------------
# Predição + histórico recente
# -------------------------
# Faz a predição do modelo e guarda o resultado em um buffer (vetor_saida).
# O buffer serve para tomar decisão com base em várias predições seguidas,
# e não em uma única leitura (evita falso alarme).
def executar_predicao(vetor_padronizado, modelo_treinado, buffer_predicoes):
    # IsolationForest retorna -1 (anomalia) ou 1 (normal)
    predicao = int(modelo_treinado.predict(vetor_padronizado)[0])

    # Mantém somente as últimas 5 predições no buffer
    if len(buffer_predicoes) >= 5:
        buffer_predicoes.pop(0)

    buffer_predicoes.append(predicao)
    return predicao


# -------------------------
# Detecção de anomalia
# -------------------------
# Decide se entra em modo alerta olhando o buffer de predições.
# Só começa a decidir quando já tem 5 resultados acumulados.
def detectar_anomalia(buffer_predicoes):
    if len(buffer_predicoes) < JANELA_PREDICAO:
        return False

    qtd_anomalias = sum(1 for p in buffer_predicoes if p == -1)
    return qtd_anomalias >= JANELA_PREDICAO
