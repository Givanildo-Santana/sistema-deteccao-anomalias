from pathlib import Path
from Python.src.arduino_serial import conectar_arduino, enviar_comando_e_ler_linha
from Python.src.parser_serial import conversao_dados
from Python.src.processamento import calcular_media_movel, vetor
from Python.src.config import (
    ordem_sensores,
    campos_obrigatorios,
    campos_filtrados,

)

cabecalho_data = ",".join(campos_filtrados) + "\n"
buffer_sensores = {}
media_leituras = {}
vetor_base = []


# -------------------------
# Conexão com o Arduino
# -------------------------
# Abre a comunicação serial com o Arduino usando a porta configurada.
conexao_arduino = conectar_arduino()

numero_arquivo_global = 0
pasta = Path("../data")

pasta.mkdir(parents=True, exist_ok=True)

for item in pasta.iterdir():
    nome_arquivo = item.name
    if nome_arquivo == "dados_normais.csv":
        numero_arquivo_global = max(numero_arquivo_global, 1)

    elif nome_arquivo.startswith("dados_normais_") and item.name.endswith(".csv"):
        nome_arquivo_sem_sufixo = nome_arquivo.removesuffix(".csv")
        numero_arquivo_srt = nome_arquivo_sem_sufixo.removeprefix("dados_normais_")

        if numero_arquivo_srt.isdigit():
            numero_arquivo = int(numero_arquivo_srt)
            numero_arquivo_global = max(numero_arquivo_global,numero_arquivo)

if numero_arquivo_global == 0:
    novo_nome_arquivo = "dados_normais.csv"

else:
    novo_nome_arquivo = f"dados_normais_{numero_arquivo_global + 1}.csv"

arquivo_saida = pasta / novo_nome_arquivo
arquivo_saida.touch()

if arquivo_saida.stat().st_size == 0:
    arquivo_saida.write_text(cabecalho_data, encoding="utf-8")

else:
    with arquivo_saida.open("r", encoding="utf-8") as f:
        cabecalho = f.readline()
    if cabecalho != cabecalho_data:
        print("Cabecalho diferente do esperado ")

while True:

    # Solicita uma nova leitura ao Arduino
    dados_serial = enviar_comando_e_ler_linha(b'#01\n', conexao_arduino)

    # Converte e valida a mensagem recebida
    dados_tratado = conversao_dados(
        dados_serial,
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
        vetor_data = vetor(
            media_leituras,
            vetor_base,
            ordem_sensores
        )
        if vetor_data:
            lista_string = [str(valor) for valor in vetor_data]
            linha = ",".join(lista_string) + "\n"

            with arquivo_saida.open("a", encoding="utf-8") as f:
                f.write(linha)

    print(media_leituras)


