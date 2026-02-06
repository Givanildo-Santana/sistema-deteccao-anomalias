# -------------------------
# Conversão e validação dos dados recebidos
# -------------------------
# Recebe a linha bruta vinda do Arduino e tenta extrair os valores dos sensores.
# Só retorna dados quando a mensagem está completa e no formato esperado.
def conversao_dados(dados_brutos, campos_obrigatorios, campos_filtrados):

    # Dicionário final com os valores numéricos dos sensores
    dados_tratados = {}

    # Verifica se a mensagem segue o protocolo esperado
    # (todas as leituras válidas começam com "LEITURA|")
    if not dados_brutos.startswith("LEITURA|"):
        return None

    # Separa a mensagem em blocos usando o delimitador '|'
    dados = dados_brutos.split('|')

    # Garante que todos os campos obrigatórios estão presentes
    # Se faltar qualquer um, a leitura é descartada
    for etiqueta in campos_obrigatorios:
        if not any(dado.startswith(etiqueta) for dado in dados):
            return None

    # Extrai apenas os campos de interesse (sensores)
    # e converte os valores para float
    for dado in dados:
        for campo in campos_filtrados:
            if dado.startswith(campo + "="):
                chave, valor = dado.split("=")
                dados_tratados[chave] = float(valor)

    return dados_tratados
