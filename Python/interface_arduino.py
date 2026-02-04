from time import sleep
import serial
import time
import os
import csv
import joblib

bundle = joblib.load("modelo_anomalia.joblib")
scaler = bundle["scaler"]
model = bundle["model"]
ordem_sensores = ["MQ7","MQ2","T","U"]
#(bundle)["colunas"]  # garante mesma ordem do treino
campos_obrigatorios = ["ID=","MQ7=","MQ2=","T=","U=","S="]
campos_filtrados = ["MQ7","MQ2","T","U"]

ARQUIVO_CSV = "dados_normais.csv"

# con_arduino: Responsável por iniciar a comunicação com o arduino
def con_arduino(porta):
    con = serial.Serial(porta, 9600)
    time.sleep(2)
    return con

# controle_arduino: Responsável por enviar e receber comandos/dados do arduino
def controle_arduino(comando,conexao):
        conexao.write(comando)
        dados_brutos = conexao.readline().decode("utf-8",errors= "ignore").strip()
        return dados_brutos

# tratamento_dados: Responsável por limpar os dados recebidos
def conversao_dados(dados_brutos, campos_obrigatorios, campos_filtrados):
    dados_tratados = {}

    if not dados_brutos.startswith("LEITURA|"):
        print("Linha ignorada (não começa com LEITURA|)")
        return None

    dados = dados_brutos.split('|')

    # 1) validar se TODOS os campos obrigatórios aparecem (por prefixo)
    for etiqueta in campos_obrigatorios:
        encontrado = False
        for dado in dados:
            if dado.startswith(etiqueta):
                encontrado = True
                break
        if not encontrado:
            print("Faltou campo obrigatório:", etiqueta)
            return None  # linha incompleta

    # 2) extrair só os campos filtrados (MQ7, MQ2, T, U) e converter
    for dado in dados:
        for campo in campos_filtrados:
            if dado.startswith(campo + "="):
                chave, valor = dado.split("=")
                dados_tratados[chave] = float(valor)

    return dados_tratados

 # calcular_media_movel: Responsável pelo calculo da média dos valores dos sensores
def calcular_media_movel(dados_tratados,buffer_sensores,media_leituras):
    for sensor in dados_tratados:
        if sensor not in buffer_sensores:
            buffer_sensores[sensor] = []

        buffer_sensores[sensor].append(dados_tratados[sensor])

        if len(buffer_sensores[sensor]) > 10:
            buffer_sensores[sensor].pop(0)
        if len(buffer_sensores[sensor]) == 10:
            media_leituras[sensor] = round(sum(buffer_sensores[sensor]) / 10, 2)
    return media_leituras

def vetor(media_leituras, vetor_base):
    vetor_base.clear()
    for sensor in ordem_sensores:
        if sensor not in media_leituras:
            return None
        vetor_base.append(media_leituras[sensor])
    return vetor_base

def salvar_amostra(amostra):
    arquivo_existe = os.path.exists(ARQUIVO_CSV)

    with open(ARQUIVO_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not arquivo_existe:
            writer.writerow(ordem_sensores)

        writer.writerow(amostra)

def padronizar_dados(vetor_entrada):
    vetor_scaled = scaler.transform([vetor_entrada])
    return vetor_scaled

def predicao(vetor_padronizado,modelo_treinado, vetor_saida):

    pred = int(modelo_treinado.predict(vetor_padronizado)[0])

    if len(vetor_saida) >= 5:
        vetor_saida.pop(0)
    vetor_saida.append(pred)
    return pred

def alerta(vetor_predicoes):
    anomalia = 0

    if len(vetor_predicoes) < 5:
        return "Dados Insuficientes"

    for predicao in vetor_predicoes:
        if predicao == -1:
            anomalia += 1
    if anomalia >= 5:
        return True
    else:
        return False

buffer_sensores = {}
media_leituras = {}
vetor_base = []
vetor_predicoes = []


conexao_arduino = con_arduino("COM5")

contador = 1
while True:

    # sleep(1)
    dados_brutos = controle_arduino(b'#01\n',conexao_arduino)
    dados_tratado = conversao_dados(dados_brutos,campos_obrigatorios, campos_filtrados)
    if dados_tratado is None:
        continue
    calcular_media_movel(dados_tratado,buffer_sensores,media_leituras)

    if media_leituras:
        vetor(media_leituras, vetor_base)

        # salvar_amostra(vetor(media_leituras, vetor_base))
        vetor_scaled = padronizar_dados(vetor_base)
        predicao(vetor_scaled,model, vetor_predicoes)
        status_Alerta = alerta(vetor_predicoes)

        if status_Alerta == True:
            conexao_arduino.write(b'#03\n')
            print(status_Alerta)
        else:
            conexao_arduino.write(b'#02\n')
            print(status_Alerta)

    print(contador)
    contador += 1