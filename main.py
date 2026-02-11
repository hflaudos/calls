"""
SISTEMA DE CALLS DE INVESTIMENTO
Motor principal de análise e disparo de alertas via WhatsApp

Uso: python main.py
"""

import sys
import os
import time
import logging
import schedule
from datetime import datetime, time as dtime

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    ACOES_BR, ACOES_EUA, ETFS, FIIS, CRIPTOS, FUTUROS_B3, FUTUROS_INT,
    OPCOES_ATIVOS, MERCADO_PREDITIVO,
    HORARIO_INICIO, HORARIO_FIM, INTERVALO_MINUTOS,
    ANALISE_FINS_DE_SEMANA, HORA_RESUMO_DIARIO,
    NOTIFICAR_COMPRA, NOTIFICAR_VENDA,
    NOTIFICAR_RESUMO_DIARIO, NOTIFICAR_ERROS,
    DEBUG_MODE
)
from src.indicators import calcular_score
from src.markets import (
    buscar_dados_yfinance, buscar_dados_cripto,
    buscar_noticias, buscar_mercados_preditivos,
    analisar_opcoes_setup
)
from src.whatsapp import (
    enviar_call, enviar_alerta_opcao, enviar_mercado_preditivo,
    enviar_noticias_relevantes, enviar_resumo_diario, enviar_teste
)


# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/sistema.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Registro de calls enviadas (evita repetição em curto período)
_calls_enviadas: dict = {}
COOLDOWN_MINUTOS = 60  # Mesma call só reenvia após 60 min


# ─────────────────────────────────────────────
# CONTROLE DE HORÁRIO
# ─────────────────────────────────────────────

def horario_operacional() -> bool:
    """Verifica se está dentro do horário de operação configurado"""
    agora = datetime.now()
    
    # Verifica dia da semana (0=seg, 6=dom)
    if not ANALISE_FINS_DE_SEMANA and agora.weekday() >= 5:
        return False

    h_ini = dtime(*map(int, HORARIO_INICIO.split(":")))
    h_fim = dtime(*map(int, HORARIO_FIM.split(":")))
    return h_ini <= agora.time() <= h_fim


def pode_enviar_call(ticker: str, direcao: str) -> bool:
    """Verifica cooldown para evitar calls repetidas do mesmo ativo"""
    chave = f"{ticker}:{direcao}"
    if chave in _calls_enviadas:
        ultimo = _calls_enviadas[chave]
        minutos_passados = (datetime.now() - ultimo).seconds // 60
        if minutos_passados < COOLDOWN_MINUTOS:
            return False
    _calls_enviadas[chave] = datetime.now()
    return True


# ─────────────────────────────────────────────
# ANÁLISE DE MERCADOS
# ─────────────────────────────────────────────

def analisar_ativo_yfinance(ticker: str, categoria: str, periodo: str = "5d", intervalo: str = "15m"):
    """Analisa um ativo via Yahoo Finance e envia call se houver setup"""
    logger.info(f"Analisando {ticker} [{categoria}]...")
    
    df = buscar_dados_yfinance(ticker, periodo=periodo, intervalo=intervalo)
    if df is None:
        return None

    analise = calcular_score(df)
    analise["ticker"] = ticker

    if analise["score"] >= 65 and analise["direcao"] != "AGUARDAR":
        if pode_enviar_call(ticker, analise["direcao"]):
            logger.info(f"📡 Call emitida: {ticker} {analise['direcao']} Score={analise['score']}")
            if (analise["direcao"] == "COMPRA" and NOTIFICAR_COMPRA) or \
               (analise["direcao"] == "VENDA/SHORT" and NOTIFICAR_VENDA):
                enviar_call(ticker, analise, categoria)

    return analise


def analisar_cripto(simbolo: str):
    """Analisa criptomoeda via Binance"""
    logger.info(f"Analisando cripto {simbolo}...")
    
    df = buscar_dados_cripto(simbolo, timeframe="15m", limite=200)
    if df is None:
        return None

    analise = calcular_score(df)
    analise["ticker"] = simbolo

    if analise["score"] >= 65 and analise["direcao"] != "AGUARDAR":
        if pode_enviar_call(simbolo, analise["direcao"]):
            logger.info(f"📡 Call cripto: {simbolo} {analise['direcao']} Score={analise['score']}")
            enviar_call(simbolo, analise, "cripto")

    return analise


def analisar_opcoes():
    """Analisa setups de opções nos ativos configurados"""
    logger.info("Analisando opções...")
    for ticker in OPCOES_ATIVOS:
        df = buscar_dados_yfinance(ticker, periodo="1mo", intervalo="1d")
        if df is None:
            continue
        analise = calcular_score(df)
        setup   = analisar_opcoes_setup(ticker, df, analise)
        if setup and pode_enviar_call(ticker + ":OPCAO", setup["estrategia"]):
            logger.info(f"📡 Setup de opção detectado: {ticker} — {setup['estrategia']}")
            enviar_alerta_opcao(setup)


def analisar_mercado_preditivo():
    """Busca oportunidades no Polymarket"""
    logger.info("Buscando mercados preditivos...")
    mercados = buscar_mercados_preditivos(limite=10)
    if mercados:
        enviar_mercado_preditivo(mercados)


def analisar_noticias():
    """Busca e envia notícias relevantes"""
    logger.info("Verificando notícias...")
    noticias = buscar_noticias(max_por_feed=5)
    if noticias:
        enviar_noticias_relevantes(noticias)


# ─────────────────────────────────────────────
# CICLO PRINCIPAL DE ANÁLISE
# ─────────────────────────────────────────────

resultados_do_dia = []

def ciclo_completo():
    """Executa um ciclo completo de análise de todos os mercados"""
    if not horario_operacional():
        logger.info("Fora do horário operacional. Aguardando...")
        return

    logger.info(f"\n{'='*50}")
    logger.info(f"INICIANDO CICLO DE ANÁLISE — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    logger.info(f"{'='*50}")

    ciclo_resultados = []

    # 1. Ações BR
    logger.info("\n── AÇÕES BRASIL ──")
    for ticker in ACOES_BR:
        r = analisar_ativo_yfinance(ticker, "acoes_br")
        if r:
            ciclo_resultados.append(r)
        time.sleep(0.5)  # Rate limit

    # 2. Ações EUA
    logger.info("\n── AÇÕES EUA ──")
    for ticker in ACOES_EUA:
        r = analisar_ativo_yfinance(ticker, "acoes_eua")
        if r:
            ciclo_resultados.append(r)
        time.sleep(0.5)

    # 3. ETFs
    logger.info("\n── ETFs ──")
    for ticker in ETFS:
        r = analisar_ativo_yfinance(ticker, "etf")
        if r:
            ciclo_resultados.append(r)
        time.sleep(0.5)

    # 4. FIIs
    logger.info("\n── FIIs ──")
    for ticker in FIIS:
        r = analisar_ativo_yfinance(ticker, "fii")
        if r:
            ciclo_resultados.append(r)
        time.sleep(0.5)

    # 5. Futuros B3
    logger.info("\n── FUTUROS B3 ──")
    for ticker in FUTUROS_B3:
        r = analisar_ativo_yfinance(ticker, "futuros_b3")
        if r:
            ciclo_resultados.append(r)
        time.sleep(0.5)

    # 6. Futuros Internacionais
    logger.info("\n── FUTUROS INTERNACIONAIS ──")
    for ticker in FUTUROS_INT:
        r = analisar_ativo_yfinance(ticker, "futuros_int")
        if r:
            ciclo_resultados.append(r)
        time.sleep(0.5)

    # 7. Criptomoedas
    logger.info("\n── CRIPTOMOEDAS ──")
    for simbolo in CRIPTOS:
        r = analisar_cripto(simbolo)
        if r:
            ciclo_resultados.append(r)
        time.sleep(1)  # Binance rate limit

    # 8. Opções (análise menos frequente)
    if datetime.now().minute % 30 == 0:  # A cada 30 minutos
        analisar_opcoes()

    # 9. Notícias (a cada hora)
    if datetime.now().minute < INTERVALO_MINUTOS:
        analisar_noticias()

    # 10. Mercado Preditivo (2x por dia)
    if datetime.now().hour in [10, 15] and datetime.now().minute < INTERVALO_MINUTOS:
        if MERCADO_PREDITIVO:
            analisar_mercado_preditivo()

    resultados_do_dia.extend(ciclo_resultados)

    calls_emitidas = [r for r in ciclo_resultados if r.get("score", 0) >= 65]
    logger.info(f"\n✅ Ciclo concluído — {len(calls_emitidas)} calls emitidas de {len(ciclo_resultados)} ativos analisados")


def resumo_diario():
    """Envia resumo diário das operações"""
    if NOTIFICAR_RESUMO_DIARIO and resultados_do_dia:
        logger.info("Enviando resumo diário...")
        enviar_resumo_diario(resultados_do_dia)
        resultados_do_dia.clear()


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

def main():
    logger.info("""
╔══════════════════════════════════════════════╗
║   SISTEMA DE CALLS DE INVESTIMENTO v1.0      ║
║   Mercados: BR | EUA | Cripto | Futuros      ║
║   Alertas: WhatsApp via CallMeBot            ║
╚══════════════════════════════════════════════╝
    """)

    # Argumentos de linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == "--teste":
            logger.info("Modo teste: enviando mensagem de teste para WhatsApp...")
            ok = enviar_teste()
            print("✅ Teste enviado!" if ok else "❌ Falha no envio. Verifique config.py")
            return
        elif sys.argv[1] == "--scan":
            logger.info("Modo scan único: executando uma análise completa...")
            ciclo_completo()
            return

    # Modo contínuo (padrão)
    logger.info(f"Iniciando monitoramento contínuo...")
    logger.info(f"Intervalo: {INTERVALO_MINUTOS} minutos")
    logger.info(f"Horário: {HORARIO_INICIO} - {HORARIO_FIM}")
    logger.info(f"Ativos monitorados: {len(ACOES_BR) + len(ACOES_EUA) + len(CRIPTOS) + len(FUTUROS_B3) + len(FUTUROS_INT)}")

    # Envia mensagem de início
    enviar_teste()

    # Agenda os ciclos
    schedule.every(INTERVALO_MINUTOS).minutes.do(ciclo_completo)
    schedule.every().day.at(HORA_RESUMO_DIARIO).do(resumo_diario)

    # Executa imediatamente o primeiro ciclo
    ciclo_completo()

    # Loop principal
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
