import serial
import time
from config import PORTA_ARDUINO,BAUDRATE, TIMEOUT_SERIAL_S

# -------------------------
# Conexão com o Arduino
# -------------------------
# Recebe a porta (ex: "COM5") e retorna o objeto de conexão já pronto.
def conectar_arduino():
    conexao_arduino = serial.Serial(
        PORTA_ARDUINO,
        BAUDRATE,
        timeout=TIMEOUT_SERIAL_S
    )


    # Pequena pausa para garantir que o Arduino reinicie
    # e a comunicação fique estável antes de usar
    time.sleep(2)

    return conexao_arduino


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
def enviar_comando_e_ler_linha(comando_serial, conexao_serial):

    # Envia o comando para o Arduino
    conexao_serial.write(comando_serial)

    # Lê uma linha completa da serial (até '\n')
    # O decode converte de bytes para string
    # errors="ignore" evita erro caso venha algum caractere inválido
    dados_serial = conexao_serial.readline().decode(
        "utf-8", errors="ignore"
    ).strip()

    return dados_serial
