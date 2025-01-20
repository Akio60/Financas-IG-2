# constants.py

# Variáveis de ambiente e outras configurações
EMAIL_PASSWORD_ENV = 'EMAIL_PASSWORD'  # Nome da variável de ambiente onde está a senha do email

# Escopo para acesso ao Google Sheets
GOOGLE_SHEETS_SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Lista de colunas detalhadas
ALL_COLUMNS_DETAIL = [
    'Valor', 'Carimbo de data/hora', 'Endereço de e-mail', 'Nome completo (sem abreviações):',
    'Ano de ingresso o PPG:', 'Curso:', 'Orientador', 'Possui bolsa?', 'Qual a agência de fomento?',
    'Título do projeto do qual participa:', 'Motivo da solicitação',
    'Nome do evento ou, se atividade de campo, motivos da realização\n* caso não se trate de evento ou viagem de campo, preencher N/A',
    'Local de realização do evento', 'Período de realização da atividade. Indique as datas (dd/mm/aaaa)',
    'Descrever detalhadamente os itens a serem financiados. Por ex: inscrição em evento, diárias (para transporte, hospedagem e alimentação), passagem aérea, pagamento de análises e traduções, etc.\n',
    'Telefone de contato:', 'E-mail DAC:', 'Endereço completo (logradouro, número, bairro, cidade e estado)',
    'CPF:', 'RG/RNE:', 'Dados bancários (banco, agência e conta) '
]

# Lista de colunas
ALL_COLUMNS = [
    'EmailRecebimento', 'EmailProcessando', 'EmailCancelamento', 'EmailAutorizado', 'EmailDocumentacao',
    'EmailPago', 'Valor', 'Status', 'Ultima Atualizacao', 'Carimbo de data/hora', 'Endereço de e-mail',
    'Declaro que li e estou ciente das regras e obrigações dispostas neste formulário',
    'Nome completo (sem abreviações):', 'Ano de ingresso o PPG:', 'Curso:', 'Orientador', 'Possui bolsa?',
    'Qual a agência de fomento?', 'Título do projeto do qual participa:', 'Motivo da solicitação',
    'Nome do evento ou, se atividade de campo, motivos da realização\n* caso não se trate de evento ou viagem de campo, preencher N/A',
    'Local de realização do evento', 'Período de realização da atividade. Indique as datas (dd/mm/aaaa)',
    'Descrever detalhadamente os itens a serem financiados. Por ex: inscrição em evento, diárias (para transporte, hospedagem e alimentação), passagem aérea, pagamento de análises e traduções, etc.\n',
    'E-mail DAC:', 'Endereço completo (logradouro, número, bairro, cidade e estado)',
    'Telefone de contato:', 'CPF:', 'RG/RNE:', 'Dados bancários (banco, agência e conta) '
]

# Cores
BG_COLOR = '#e0f0ff'
BUTTON_BG_COLOR = '#add8e6'
FRAME_BG_COLOR = '#d0e0ff'

STATUS_COLORS = {
    'Aguardando documentação': '#B8860B',  # DarkGoldenrod
    'Autorizado': '#006400',               # DarkGreen
    'Negado': '#8B0000',                   # DarkRed
    'Pronto para pagamento': '#00008B',    # DarkBlue
    'Pago': '#4B0082',                     # Indigo
    'Cancelado': '#696969',                # DimGray
}

# Mapeamento de nomes de colunas para exibição
COLUMN_DISPLAY_NAMES = {
    'Carimbo de data/hora_str': 'Data do requerimento',
    # Adicione outros mapeamentos se necessário
}
