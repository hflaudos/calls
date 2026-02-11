"""
Motor de Indicadores Técnicos
Calcula RSI, MACD, Bollinger Bands, EMAs, Volume e gera score de entrada
"""

import pandas as pd
import numpy as np
from config import (
    RSI_PERIODO, RSI_SOBRECOMPRADO, RSI_SOBREVENDIDO,
    MACD_RAPIDA, MACD_LENTA, MACD_SINAL,
    BB_PERIODO, BB_DESVIO,
    EMA_CURTA, EMA_MEDIA, EMA_LONGA,
    VOLUME_MEDIA_PERIODOS, VOLUME_SPIKE_FATOR
)


def calcular_rsi(precos: pd.Series, periodo: int = RSI_PERIODO) -> pd.Series:
    delta = precos.diff()
    ganho = delta.clip(lower=0)
    perda = -delta.clip(upper=0)
    media_ganho = ganho.ewm(com=periodo - 1, min_periods=periodo).mean()
    media_perda = perda.ewm(com=periodo - 1, min_periods=periodo).mean()
    rs = media_ganho / media_perda
    return 100 - (100 / (1 + rs))


def calcular_macd(precos: pd.Series):
    ema_rapida = precos.ewm(span=MACD_RAPIDA, adjust=False).mean()
    ema_lenta  = precos.ewm(span=MACD_LENTA,  adjust=False).mean()
    macd_linha = ema_rapida - ema_lenta
    sinal      = macd_linha.ewm(span=MACD_SINAL, adjust=False).mean()
    histograma = macd_linha - sinal
    return macd_linha, sinal, histograma


def calcular_bollinger(precos: pd.Series):
    media  = precos.rolling(BB_PERIODO).mean()
    desvio = precos.rolling(BB_PERIODO).std()
    banda_sup = media + (BB_DESVIO * desvio)
    banda_inf = media - (BB_DESVIO * desvio)
    return banda_sup, media, banda_inf


def calcular_emas(precos: pd.Series):
    ema_c = precos.ewm(span=EMA_CURTA,  adjust=False).mean()
    ema_m = precos.ewm(span=EMA_MEDIA,  adjust=False).mean()
    ema_l = precos.ewm(span=EMA_LONGA,  adjust=False).mean()
    return ema_c, ema_m, ema_l


def calcular_atr(df: pd.DataFrame, periodo: int = 14) -> pd.Series:
    """Average True Range - mede volatilidade para calcular stop/target"""
    high, low, close = df['high'], df['low'], df['close']
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low  - close.shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(periodo).mean()


def calcular_volume_spike(volume: pd.Series) -> pd.Series:
    media = volume.rolling(VOLUME_MEDIA_PERIODOS).mean()
    return volume / media


def detectar_divergencia(precos: pd.Series, rsi: pd.Series, janela: int = 5) -> str:
    """Detecta divergências altistas/baixistas entre preço e RSI"""
    if len(precos) < janela * 2:
        return "neutro"
    
    preco_recente = precos.iloc[-janela:]
    rsi_recente   = rsi.iloc[-janela:]
    
    # Divergência altista: preço fazendo mínimas menores, RSI fazendo mínimas maiores
    if preco_recente.iloc[-1] < preco_recente.iloc[0] and rsi_recente.iloc[-1] > rsi_recente.iloc[0]:
        return "altista"
    
    # Divergência baixista: preço fazendo máximas maiores, RSI fazendo máximas menores
    if preco_recente.iloc[-1] > preco_recente.iloc[0] and rsi_recente.iloc[-1] < rsi_recente.iloc[0]:
        return "baixista"
    
    return "neutro"


def calcular_score(df: pd.DataFrame) -> dict:
    """
    Motor principal de scoring.
    Retorna um dict com score (0-100), direção, e sinais individuais.
    """
    if df is None or len(df) < max(MACD_LENTA + MACD_SINAL, BB_PERIODO, EMA_LONGA) + 5:
        return {"score": 0, "direcao": "aguardar", "sinais": []}

    close  = df['close']
    volume = df['volume']
    preco_atual = close.iloc[-1]

    # --- Calcular indicadores ---
    rsi            = calcular_rsi(close)
    macd, sinal_m, hist = calcular_macd(close)
    bb_sup, bb_med, bb_inf = calcular_bollinger(close)
    ema_c, ema_m, ema_l = calcular_emas(close)
    atr            = calcular_atr(df)
    vol_spike      = calcular_volume_spike(volume)
    divergencia    = detectar_divergencia(close, rsi)

    # Valores atuais
    rsi_atual  = rsi.iloc[-1]
    rsi_prev   = rsi.iloc[-2]
    hist_atual = hist.iloc[-1]
    hist_prev  = hist.iloc[-2]
    vol_atual  = vol_spike.iloc[-1]
    atr_atual  = atr.iloc[-1]
    
    pontos_compra  = 0
    pontos_venda   = 0
    sinais = []

    # ===== SINAIS DE COMPRA =====

    # RSI saindo de sobrevenda
    if rsi_atual < RSI_SOBREVENDIDO:
        pontos_compra += 20
        sinais.append(f"🟢 RSI SOBREVENDIDO ({rsi_atual:.1f}) — Possível reversão altista")
    elif rsi_prev < RSI_SOBREVENDIDO and rsi_atual >= RSI_SOBREVENDIDO:
        pontos_compra += 25
        sinais.append(f"🟢 RSI SAINDO DE SOBREVENDA ({rsi_atual:.1f}) — Sinal de entrada")

    # MACD cruzando para cima
    if hist_prev < 0 and hist_atual > 0:
        pontos_compra += 25
        sinais.append(f"🟢 MACD CRUZAMENTO ALTISTA — Histograma virou positivo")
    elif hist_atual > 0 and hist_atual > hist_prev:
        pontos_compra += 10
        sinais.append(f"🟢 MACD fortalecendo (histograma crescendo)")

    # Preço tocando/abaixo da banda inferior de Bollinger
    if preco_atual <= bb_inf.iloc[-1]:
        pontos_compra += 20
        sinais.append(f"🟢 BOLLINGER: Preço na banda inferior (possível bounce)")

    # Alinhamento de EMAs bullish
    if ema_c.iloc[-1] > ema_m.iloc[-1] > ema_l.iloc[-1]:
        pontos_compra += 15
        sinais.append(f"🟢 EMAs ALINHADAS BULLISH ({EMA_CURTA}/{EMA_MEDIA}/{EMA_LONGA})")
    elif ema_c.iloc[-1] > ema_m.iloc[-1] and ema_c.iloc[-2] <= ema_m.iloc[-2]:
        pontos_compra += 20
        sinais.append(f"🟢 CRUZAMENTO EMA {EMA_CURTA} ACIMA DE {EMA_MEDIA} — Golden cross curto")

    # Volume spike + movimento de alta
    if vol_atual >= VOLUME_SPIKE_FATOR and close.iloc[-1] > close.iloc[-2]:
        pontos_compra += 15
        sinais.append(f"🟢 VOLUME SPIKE {vol_atual:.1f}x acima da média com candle de alta")

    # Divergência altista
    if divergencia == "altista":
        pontos_compra += 15
        sinais.append("🟢 DIVERGÊNCIA ALTISTA entre Preço e RSI")

    # ===== SINAIS DE VENDA/SHORT =====

    # RSI sobrecomprado
    if rsi_atual > RSI_SOBRECOMPRADO:
        pontos_venda += 20
        sinais.append(f"🔴 RSI SOBRECOMPRADO ({rsi_atual:.1f}) — Possível reversão baixista")
    elif rsi_prev > RSI_SOBRECOMPRADO and rsi_atual <= RSI_SOBRECOMPRADO:
        pontos_venda += 25
        sinais.append(f"🔴 RSI SAINDO DE SOBRECOMPRA ({rsi_atual:.1f}) — Sinal de saída/short")

    # MACD cruzando para baixo
    if hist_prev > 0 and hist_atual < 0:
        pontos_venda += 25
        sinais.append(f"🔴 MACD CRUZAMENTO BAIXISTA — Histograma virou negativo")

    # Preço tocando/acima da banda superior de Bollinger
    if preco_atual >= bb_sup.iloc[-1]:
        pontos_venda += 20
        sinais.append(f"🔴 BOLLINGER: Preço na banda superior (possível topo)")

    # EMAs bearish
    if ema_c.iloc[-1] < ema_m.iloc[-1] < ema_l.iloc[-1]:
        pontos_venda += 15
        sinais.append(f"🔴 EMAs ALINHADAS BEARISH")

    # Volume spike + queda
    if vol_atual >= VOLUME_SPIKE_FATOR and close.iloc[-1] < close.iloc[-2]:
        pontos_venda += 15
        sinais.append(f"🔴 VOLUME SPIKE {vol_atual:.1f}x acima da média com candle de baixa")

    # Divergência baixista
    if divergencia == "baixista":
        pontos_venda += 15
        sinais.append("🔴 DIVERGÊNCIA BAIXISTA entre Preço e RSI")

    # ===== CALCULAR STOP/TARGET VIA ATR =====
    stop_compra    = round(preco_atual - (atr_atual * 1.5), 4)
    target_compra  = round(preco_atual + (atr_atual * 3.0), 4)
    stop_venda     = round(preco_atual + (atr_atual * 1.5), 4)
    target_venda   = round(preco_atual - (atr_atual * 3.0), 4)

    # ===== DECISÃO FINAL =====
    if pontos_compra > pontos_venda:
        score    = min(pontos_compra, 100)
        direcao  = "COMPRA"
        stop     = stop_compra
        target   = target_compra
    elif pontos_venda > pontos_compra:
        score    = min(pontos_venda, 100)
        direcao  = "VENDA/SHORT"
        stop     = stop_venda
        target   = target_venda
    else:
        score    = 0
        direcao  = "AGUARDAR"
        stop     = None
        target   = None

    return {
        "score":     score,
        "direcao":   direcao,
        "preco":     preco_atual,
        "stop":      stop,
        "target":    target,
        "rsi":       round(rsi_atual, 1),
        "sinais":    sinais,
        "pontos_c":  pontos_compra,
        "pontos_v":  pontos_venda,
    }
