import serial
import time

# -------------------------
# Conexão com o Arduino
# -------------------------
# Responsável por abrir a comunicação serial com o Arduino.
# Recebe a porta (ex: "COM5") e retorna o objeto de conexão já pronto.
def con_arduino(porta):
    # Abre a porta serial na velocidade configurada no Arduino (9600)
    con = serial.Serial(porta, 9600)

    # Pequena pausa para garantir que o Arduino reinicie
    # e a comunicação fique estável antes de usar
    time.sleep(2)

    return con


# -------------------------
# Controle de comunicação Serial
# -------------------------
# Envia um comando para o Arduino e aguarda uma resposta.
#
# Parâmetros:
# - comando: bytes enviados (ex: b"#01\n")
# - conexao: objeto Serial já aberto
#
# Retorno:
# - string com a linha recebida do Arduino
def controle_arduino(comando, conexao):

    # Envia o comando para o Arduino
    conexao.write(comando)

    # Lê uma linha completa da serial (até '\n')
    # O decode converte de bytes para string
    # errors="ignore" evita erro caso venha algum caractere inválido
    dados_brutos = conexao.readline().decode(
        "utf-8", errors="ignore"
    ).strip()

    return dados_brutos
