# ============================================================
#   ARQUIVO DE CONFIGURAÇÃO - EDITE APENAS ESTE ARQUIVO
# ============================================================
# Siga o GUIA_DE_CONFIGURACAO.md para preencher corretamente

# --- WHATSAPP (CallMeBot - GRATUITO) ---
# Siga o passo a passo no guia para obter sua API KEY
WHATSAPP_NUMBER = "+5511999999999"   # Seu número com DDI (ex: +5511988887777)
CALLMEBOT_APIKEY = "COLE_SUA_KEY_AQUI"

# --- HORÁRIO DE OPERAÇÃO ---
# Define quando o sistema está ativo (horário de Brasília)
HORARIO_INICIO = "09:00"     # Início das análises
HORARIO_FIM    = "18:00"     # Fim das análises (mercado B3)
ANALISE_FINS_DE_SEMANA = True  # Ativar para cripto (funciona 24/7)

# --- INTERVALO ENTRE ANÁLISES ---
INTERVALO_MINUTOS = 15  # A cada quantos minutos o sistema verifica o mercado

# --- ATIVOS MONITORADOS ---
# Ações BR (sufixo .SA obrigatório)
ACOES_BR = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA",
    "WEGE3.SA", "MGLU3.SA", "BBAS3.SA", "ABEV3.SA",
    "B3SA3.SA", "RENT3.SA"
]

# Ações EUA
ACOES_EUA = [
    "AAPL", "TSLA", "NVDA", "MSFT",
    "AMZN", "GOOGL", "META", "SPY", "QQQ"
]

# ETFs
ETFS = ["BOVA11.SA", "IVVB11.SA", "HASH11.SA", "SMAL11.SA"]

# Fundos Imobiliários (FIIs)
FIIS = ["MXRF11.SA", "KNRI11.SA", "XPML11.SA", "HGLG11.SA"]

# Criptomoedas (pares USDT na Binance)
CRIPTOS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT",
    "ADA/USDT", "XRP/USDT", "DOGE/USDT", "AVAX/USDT"
]

# Futuros B3 (mini-índice e mini-dólar)
# WIN = mini-índice Bovespa | WDO = mini-dólar
FUTUROS_B3 = ["WINFUT.SA", "WDOFUT.SA"]

# Futuros internacionais
FUTUROS_INT = [
    "GC=F",   # Ouro
    "SI=F",   # Prata
    "CL=F",   # Petróleo WTI
    "ES=F",   # S&P 500 Futuro
    "NQ=F",   # Nasdaq Futuro
]

# Opções (o sistema monitora as ações-mãe e alerta quando há setup)
OPCOES_ATIVOS = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA"]

# Mercado Preditivo (Polymarket - eventos monitorados via RSS/API)
MERCADO_PREDITIVO = True

# --- CONFIGURAÇÕES DE RISCO ---
# Score mínimo para emitir call (0-100). Recomendado 70+ para day trade especulativo
SCORE_MINIMO_CALL = 65

# Stop loss sugerido padrão (% abaixo do ponto de entrada)
STOP_LOSS_PADRAO_PCT = 2.0

# Take profit sugerido padrão (% acima do ponto de entrada)
TAKE_PROFIT_PADRAO_PCT = 4.0

# --- INDICADORES TÉCNICOS (períodos) ---
RSI_PERIODO = 14
RSI_SOBRECOMPRADO = 70
RSI_SOBREVENDIDO = 30
MACD_RAPIDA = 12
MACD_LENTA = 26
MACD_SINAL = 9
BB_PERIODO = 20
BB_DESVIO = 2
EMA_CURTA = 9
EMA_MEDIA = 21
EMA_LONGA = 50
VOLUME_MEDIA_PERIODOS = 20
VOLUME_SPIKE_FATOR = 2.0  # Volume X vezes acima da média = sinal relevante

# --- NOTIFICAÇÕES ---
NOTIFICAR_COMPRA = True
NOTIFICAR_VENDA = True
NOTIFICAR_RESUMO_DIARIO = True
HORA_RESUMO_DIARIO = "17:30"  # Resumo do dia
NOTIFICAR_ERROS = True  # Receber alertas de erro do sistema

# --- MODO DEBUG ---
DEBUG_MODE = False  # True = mostra logs detalhados no terminal
