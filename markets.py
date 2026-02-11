"""
Módulo de Coleta de Dados de Mercado
Busca dados em tempo real de: Yahoo Finance (ações/futuros/ETFs) e Binance (cripto)
"""

import time
import logging
import pandas as pd
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    yf = None

try:
    import ccxt
except ImportError:
    ccxt = None

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  AÇÕES / ETFs / FIIs / FUTUROS (Yahoo Finance)
# ─────────────────────────────────────────────

def buscar_dados_yfinance(ticker: str, periodo: str = "5d", intervalo: str = "15m") -> pd.DataFrame | None:
    """
    Busca dados OHLCV via Yahoo Finance.
    
    periodo:   1d, 5d, 1mo, 3mo
    intervalo: 1m, 5m, 15m, 30m, 1h, 1d
    """
    if yf is None:
        logger.error("yfinance não instalado. Execute: pip install yfinance")
        return None
    try:
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period=periodo, interval=intervalo)
        if df.empty:
            logger.warning(f"Sem dados para {ticker}")
            return None
        df.columns = [c.lower() for c in df.columns]
        df = df[['open', 'high', 'low', 'close', 'volume']].copy()
        df.dropna(inplace=True)
        return df
    except Exception as e:
        logger.error(f"Erro ao buscar {ticker}: {e}")
        return None


def buscar_info_fundamental(ticker: str) -> dict:
    """Busca dados fundamentalistas básicos via Yahoo Finance"""
    if yf is None:
        return {}
    try:
        info = yf.Ticker(ticker).info
        return {
            "nome":          info.get("longName", ticker),
            "setor":         info.get("sector", "N/A"),
            "pe_ratio":      info.get("trailingPE", None),
            "pb_ratio":      info.get("priceToBook", None),
            "dividend_yield":info.get("dividendYield", None),
            "market_cap":    info.get("marketCap", None),
            "52w_high":      info.get("fiftyTwoWeekHigh", None),
            "52w_low":       info.get("fiftyTwoWeekLow", None),
            "beta":          info.get("beta", None),
            "preco_atual":   info.get("currentPrice", info.get("regularMarketPrice", None)),
        }
    except Exception as e:
        logger.warning(f"Fundamentalista indisponível para {ticker}: {e}")
        return {}


# ─────────────────────────────────────────────
#  CRIPTOMOEDAS (Binance via ccxt)
# ─────────────────────────────────────────────

_exchange_binance = None

def _get_binance():
    global _exchange_binance
    if _exchange_binance is None and ccxt is not None:
        _exchange_binance = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
    return _exchange_binance


def buscar_dados_cripto(simbolo: str, timeframe: str = "15m", limite: int = 200) -> pd.DataFrame | None:
    """
    Busca OHLCV de criptomoeda na Binance.
    simbolo:   "BTC/USDT", "ETH/USDT", etc.
    timeframe: "1m", "5m", "15m", "1h", "4h", "1d"
    """
    if ccxt is None:
        logger.error("ccxt não instalado. Execute: pip install ccxt")
        return None
    try:
        exchange = _get_binance()
        ohlcv    = exchange.fetch_ohlcv(simbolo, timeframe=timeframe, limit=limite)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        logger.error(f"Erro ao buscar cripto {simbolo}: {e}")
        return None


def buscar_funding_rate(simbolo: str) -> float | None:
    """Busca funding rate do mercado de futuros perpétuos da Binance"""
    if ccxt is None:
        return None
    try:
        exchange = ccxt.binance({'options': {'defaultType': 'future'}})
        fr = exchange.fetch_funding_rate(simbolo.replace('/', ''))
        return fr.get('fundingRate', None)
    except:
        return None


# ─────────────────────────────────────────────
#  MERCADO PREDITIVO (Polymarket via API pública)
# ─────────────────────────────────────────────

def buscar_mercados_preditivos(limite: int = 10) -> list:
    """Busca top mercados do Polymarket com maior volume"""
    try:
        import requests
        url = "https://gamma-api.polymarket.com/markets"
        params = {
            "active": "true",
            "closed": "false",
            "limit":  limite,
            "order":  "volume24hr",
            "ascending": "false"
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return []
        mercados = resp.json()
        resultado = []
        for m in mercados:
            resultado.append({
                "pergunta":   m.get("question", ""),
                "volume_24h": m.get("volume24hr", 0),
                "preco_sim":  m.get("outcomePrices", ["N/A"])[0] if m.get("outcomePrices") else "N/A",
                "preco_nao":  m.get("outcomePrices", ["N/A", "N/A"])[1] if m.get("outcomePrices") and len(m.get("outcomePrices", [])) > 1 else "N/A",
                "liquidity":  m.get("liquidity", 0),
                "url":        f"https://polymarket.com/event/{m.get('slug', '')}",
            })
        return resultado
    except Exception as e:
        logger.warning(f"Erro ao buscar Polymarket: {e}")
        return []


# ─────────────────────────────────────────────
#  NOTÍCIAS (RSS via feedparser)
# ─────────────────────────────────────────────

FEEDS_NOTICIAS = {
    "InfoMoney":      "https://www.infomoney.com.br/feed/",
    "Investing.com":  "https://br.investing.com/rss/news.rss",
    "CoinTelegraph":  "https://cointelegraph.com/rss",
    "Bloomberg":      "https://feeds.bloomberg.com/markets/news.rss",
}

PALAVRAS_CHAVE_RELEVANTES = [
    "ibovespa", "bovespa", "bitcoin", "ethereum", "fed", "selic",
    "juros", "inflação", "cpi", "gdp", "earnings", "resultado",
    "petrobras", "vale", "bank", "crash", "rally", "alta", "queda",
    "ipca", "copom", "dólar", "real", "commodities", "ouro", "petróleo"
]

def buscar_noticias(max_por_feed: int = 5) -> list:
    """Busca notícias financeiras relevantes via RSS"""
    try:
        import feedparser
    except ImportError:
        logger.warning("feedparser não instalado. Execute: pip install feedparser")
        return []

    noticias = []
    for fonte, url in FEEDS_NOTICIAS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_por_feed]:
                titulo = entry.get('title', '').lower()
                if any(kw in titulo for kw in PALAVRAS_CHAVE_RELEVANTES):
                    noticias.append({
                        "fonte":  fonte,
                        "titulo": entry.get('title', ''),
                        "link":   entry.get('link', ''),
                        "data":   entry.get('published', ''),
                    })
        except Exception as e:
            logger.warning(f"Erro ao buscar feed {fonte}: {e}")
    return noticias[:10]  # Limita a 10 mais relevantes


# ─────────────────────────────────────────────
#  OPÇÕES (análise baseada no ativo-mãe)
# ─────────────────────────────────────────────

def analisar_opcoes_setup(ticker: str, df: pd.DataFrame, score_ativo: dict) -> dict | None:
    """
    Analisa se há setup de opções baseado no movimento do ativo-mãe.
    Sugere estratégias simples: compra de call/put ou trava.
    """
    if df is None or score_ativo["score"] < 60:
        return None

    preco = score_ativo["preco"]
    direcao = score_ativo["direcao"]

    # Calcular volatilidade implícita aproximada (via desvio padrão histórico)
    retornos = df['close'].pct_change().dropna()
    vol_hist = retornos.std() * (252 ** 0.5)  # Anualizada

    estrategia = None
    descricao   = ""

    if direcao == "COMPRA":
        if vol_hist < 0.30:  # Baixa volatilidade: comprar call direta
            estrategia = "COMPRA DE CALL"
            descricao  = f"Comprar CALL OTM ~5% acima do preço atual (strike ~R${preco*1.05:.2f})"
        else:  # Alta vol: usar trava de alta para reduzir custo
            estrategia = "TRAVA DE ALTA (CALL SPREAD)"
            descricao  = (f"Comprar CALL strike R${preco*1.02:.2f} + "
                          f"Vender CALL strike R${preco*1.07:.2f}")
    elif direcao == "VENDA/SHORT":
        if vol_hist < 0.30:
            estrategia = "COMPRA DE PUT"
            descricao  = f"Comprar PUT OTM ~5% abaixo do preço atual (strike ~R${preco*0.95:.2f})"
        else:
            estrategia = "TRAVA DE BAIXA (PUT SPREAD)"
            descricao  = (f"Comprar PUT strike R${preco*0.98:.2f} + "
                          f"Vender PUT strike R${preco*0.93:.2f}")

    return {
        "ativo":      ticker,
        "estrategia": estrategia,
        "descricao":  descricao,
        "vol_hist":   round(vol_hist * 100, 1),
    }
