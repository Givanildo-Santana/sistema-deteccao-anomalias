"""
Tempo real (Arduino -> IA) usando o modelo treinado em modelo_anomalia.joblib

O que faz:
- Conecta no Arduino via Serial
- Lê linhas no formato: "MQ2:123|MQ7:456|temperatura:25|umidade:60"
- Aplica média móvel (janela de 10) igual ao seu coletor
- Monta vetor na ordem correta
- Padroniza com o scaler treinado
- Classifica com IsolationForest (1 = normal, -1 = anomalia)
- Usa "debounce": só dispara ALERTA após N anomalias seguidas
- Loga alertas em CSV separado

Ajuste:
- PORTA_SERIAL (ex: "COM5")
- BAUD (9600)
- ANOM_ALIAS_SEGUIDAS (ex: 3)
- JANELA_MEDIA (10)
"""

import time
import csv
import os
import serial
import joblib
import numpy as np
from datetime import datetime

# ======================
# CONFIGURAÇÕES
# ======================
PORTA_SERIAL = "COM5"
BAUD = 9600
TIMEOUT_SERIAL = 2

COMANDO = b"#01\n"
TEXTO_IGNORAR = "Comando Recebido: CMD_ENVIAR_LEITURA"

JANELA_MEDIA = 10               # média móvel de 10 leituras
ANOM_ALIAS_SEGUIDAS = 3         # quantas anomalias seguidas pra disparar alerta
INTERVALO_ENTRE_LEITURAS = 0.2  # segundos (ajuste conforme seu Arduino)

ARQ_MODELO = "modelo_anomalia.joblib"
ARQ_LOG_ALERTAS = "alertas.csv"


# ======================
# FUNÇÕES AUXILIARES
# ======================
def con_arduino(porta: str) -> serial.Serial:
    con = serial.Serial(porta, BAUD, timeout=TIMEOUT_SERIAL)
    time.sleep(2)  # tempo pro Arduino resetar
    return con


def controle_arduino(comando: bytes, conexao: serial.Serial, ignore: str) -> str:
    conexao.write(comando)
    linha = conexao.readline().decode("utf-8", errors="ignore").strip()
    if ignore:
        linha = linha.replace(ignore, "").strip()
    return linha


def tratamento_dados(dados_brutos: str) -> dict:
    """
    Espera algo como:
    "MQ2:123|MQ7:456|temperatura:25|umidade:60"
    Retorna dict com floats.
    """
    dados_brutos = dados_brutos.strip()
    if not dados_brutos:
        raise ValueError("Linha vazia após limpeza")

    partes = dados_brutos.split("|")
    dados_tratados = {}
    for p in partes:
        if not p:
            continue
        if ":" not in p:
            raise ValueError(f"Formato inválido (sem ':'): {p}")
        chave, valor = p.split(":", 1)
        chave = chave.strip()
        valor = valor.strip().replace(",", ".")
        dados_tratados[chave] = float(valor)
    return dados_tratados


def calcular_media_movel(dicionario: dict, buffer_sensores: dict, media_leituras: dict, janela: int) -> dict:
    """
    Mantém buffer por sensor e calcula média quando tiver 'janela' valores.
    """
    for sensor, valor in dicionario.items():
        if sensor not in buffer_sensores:
            buffer_sensores[sensor] = []
        buffer_sensores[sensor].append(valor)

        if len(buffer_sensores[sensor]) >= janela:
            media = sum(buffer_sensores[sensor][-janela:]) / janela
            media_leituras[sensor] = round(media, 3)

            # Mantém buffer sem crescer pra sempre
            if len(buffer_sensores[sensor]) > janela * 3:
                buffer_sensores[sensor] = buffer_sensores[sensor][-janela * 2 :]

    return media_leituras


def vetor(dicionario_valor: dict, ordem_sensores: list) -> list | None:
    """
    Retorna vetor na ordem, ou None se faltar algum sensor.
    """
    v = []
    for sensor in ordem_sensores:
        if sensor not in dicionario_valor:
            return None
        v.append(dicionario_valor[sensor])
    return v


def log_alerta(csv_path: str, colunas: list[str], amostra: list[float], score: float, pred: int):
    existe = os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow(["timestamp"] + colunas + ["score", "pred"])
        w.writerow([datetime.now().isoformat(timespec="seconds")] + amostra + [round(score, 6), int(pred)])


# ======================
# MAIN
# ======================
def main():
    # 1) Carrega modelo + scaler + ordem de colunas
    bundle = joblib.load(ARQ_MODELO)
    scaler = bundle["scaler"]
    model = bundle["model"]
    colunas = bundle.get("colunas", ["MQ2", "MQ7", "temperatura", "umidade"])

    # 2) Conecta Arduino
    conexao = con_arduino(PORTA_SERIAL)

    # 3) Buffers / estado
    buffer_sensores = {}
    media_leituras = {}

    anom_consecutivas = 0
    total_lidas = 0
    total_validas = 0
    total_anomalias = 0

    print("=== Monitoramento em tempo real iniciado ===")
    print(f"Porta: {PORTA_SERIAL} | Baud: {BAUD}")
    print(f"Colunas/ordem: {colunas}")
    print("CTRL+C para parar.\n")

    try:
        while True:
            total_lidas += 1

            # Lê linha do Arduino
            linha = controle_arduino(COMANDO, conexao, TEXTO_IGNORAR)

            # Se veio vazia ou lixo, pula
            if not linha or "CMD_ENVIAR_LEITURA" in linha:
                time.sleep(INTERVALO_ENTRE_LEITURAS)
                continue

            # Parse + média móvel
            try:
                dados = tratamento_dados(linha)
                calcular_media_movel(dados, buffer_sensores, media_leituras, JANELA_MEDIA)
            except Exception as e:
                print(f"[WARN] Linha inválida: {linha!r} | erro={e}")
                time.sleep(INTERVALO_ENTRE_LEITURAS)
                continue

            # Só classifica quando tiver média para todas as colunas
            amostra = vetor(media_leituras, colunas)
            if amostra is None:
                # ainda juntando janela ou faltou campo
                time.sleep(INTERVALO_ENTRE_LEITURAS)
                continue

            total_validas += 1

            # 4) Prepara e classifica
            x = np.array(amostra, dtype=float).reshape(1, -1)
            x_scaled = scaler.transform(x)

            pred = int(model.predict(x_scaled)[0])  # 1 normal, -1 anomalia
            score = float(model.decision_function(x_scaled)[0])  # maior = mais normal (em geral)

            if pred == -1:
                total_anomalias += 1
                anom_consecutivas += 1
            else:
                anom_consecutivas = 0

            # 5) Saída no console + debounce
            status = "OK"
            if anom_consecutivas >= ANOM_ALIAS_SEGUIDAS:
                status = "ALERTA"
                log_alerta(ARQ_LOG_ALERTAS, colunas, amostra, score, pred)

            print(
                f"{status:6} | pred={pred:2d} | score={score: .6f} | "
                f"MQ2={amostra[0]:8.3f} MQ7={amostra[1]:8.3f} T={amostra[2]:6.3f} U={amostra[3]:6.3f} | "
                f"anom_seq={anom_consecutivas} | validas={total_validas}"
            )

            time.sleep(INTERVALO_ENTRE_LEITURAS)

    except KeyboardInterrupt:
        print("\nParando...")
    finally:
        try:
            conexao.close()
        except Exception:
            pass

    print("\n=== Resumo ===")
    print(f"Linhas lidas: {total_lidas}")
    print(f"Amostras válidas (com média): {total_validas}")
    print(f"Anomalias detectadas: {total_anomalias}")
    print(f"Alertas logados em: {ARQ_LOG_ALERTAS}")


if __name__ == "__main__":
    main()
