"""
Módulo de Notificações via WhatsApp
Usa CallMeBot (GRATUITO) para enviar mensagens direto no WhatsApp
"""

import requests
import logging
import urllib.parse
from datetime import datetime
from config import WHATSAPP_NUMBER, CALLMEBOT_APIKEY, SCORE_MINIMO_CALL

logger = logging.getLogger(__name__)

# Emojis por categoria de ativo
EMOJI_CATEGORIA = {
    "acoes_br":    "🇧🇷",
    "acoes_eua":   "🇺🇸",
    "cripto":      "🪙",
    "futuros_b3":  "📊",
    "futuros_int": "🌍",
    "etf":         "📦",
    "fii":         "🏢",
    "opcoes":      "🎯",
    "preditivo":   "🔮",
}

EMOJI_DIRECAO = {
    "COMPRA":       "🟢📈",
    "VENDA/SHORT":  "🔴📉",
    "AGUARDAR":     "⚪⏳",
}


def _enviar_whatsapp(mensagem: str) -> bool:
    """Envia mensagem via CallMeBot API"""
    if CALLMEBOT_APIKEY == "COLE_SUA_KEY_AQUI":
        logger.warning("CallMeBot API KEY não configurada! Verifique config.py")
        print(f"\n[SIMULAÇÃO WhatsApp]\n{mensagem}\n{'─'*50}")
        return True  # Simula envio para testes

    try:
        numero   = WHATSAPP_NUMBER.replace("+", "").replace(" ", "")
        msg_enc  = urllib.parse.quote(mensagem)
        url      = f"https://api.callmebot.com/whatsapp.php?phone={numero}&text={msg_enc}&apikey={CALLMEBOT_APIKEY}"
        
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            logger.info(f"WhatsApp enviado com sucesso")
            return True
        else:
            logger.error(f"Erro CallMeBot: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Falha ao enviar WhatsApp: {e}")
        return False


def formatar_call(ticker: str, analise: dict, categoria: str) -> str:
    """Formata a mensagem de call de investimento"""
    emoji_cat = EMOJI_CATEGORIA.get(categoria, "📌")
    emoji_dir = EMOJI_DIRECAO.get(analise["direcao"], "⚪")
    agora     = datetime.now().strftime("%d/%m %H:%M")

    # Cabeçalho
    linhas = [
        f"{'═'*30}",
        f"{emoji_cat} *CALL — {ticker}*",
        f"{emoji_dir} *{analise['direcao']}*  |  Score: {analise['score']}/100",
        f"🕐 {agora}",
        f"{'─'*30}",
    ]

    # Preço e níveis
    preco = analise.get("preco")
    if preco:
        linhas.append(f"💰 *Entrada:* {formatar_preco(preco, categoria)}")
    if analise.get("stop"):
        linhas.append(f"🛑 *Stop Loss:* {formatar_preco(analise['stop'], categoria)}")
    if analise.get("target"):
        linhas.append(f"🎯 *Take Profit:* {formatar_preco(analise['target'], categoria)}")
    if analise.get("rsi"):
        linhas.append(f"📉 *RSI:* {analise['rsi']}")

    # Sinais que dispararam a call
    if analise.get("sinais"):
        linhas.append(f"{'─'*30}")
        linhas.append("📡 *Sinais:*")
        for s in analise["sinais"][:4]:  # Máximo 4 sinais para não encher o zap
            linhas.append(f"  {s}")

    linhas.append(f"{'═'*30}")
    linhas.append("⚠️ _Não é recomendação. Use seu critério._")

    return "\n".join(linhas)


def formatar_preco(preco: float, categoria: str) -> str:
    """Formata o preço de acordo com a categoria do ativo"""
    if categoria == "cripto":
        if preco > 1000:
            return f"${preco:,.2f}"
        elif preco > 1:
            return f"${preco:.4f}"
        else:
            return f"${preco:.6f}"
    elif categoria in ("acoes_eua", "futuros_int", "etf"):
        return f"${preco:.2f}"
    else:
        return f"R${preco:.2f}"


def enviar_call(ticker: str, analise: dict, categoria: str) -> bool:
    """Envia call de investimento se score atingir o mínimo"""
    if analise["score"] < SCORE_MINIMO_CALL:
        return False
    if analise["direcao"] == "AGUARDAR":
        return False

    mensagem = formatar_call(ticker, analise, categoria)
    return _enviar_whatsapp(mensagem)


def enviar_alerta_opcao(info_opcao: dict) -> bool:
    """Envia alerta de setup de opções"""
    agora = datetime.now().strftime("%d/%m %H:%M")
    msg = (
        f"{'═'*30}\n"
        f"🎯 *SETUP DE OPÇÕES — {info_opcao['ativo']}*\n"
        f"🕐 {agora}\n"
        f"{'─'*30}\n"
        f"📋 *Estratégia:* {info_opcao['estrategia']}\n"
        f"📝 *Como montar:*\n  {info_opcao['descricao']}\n"
        f"📊 *Vol. Histórica:* {info_opcao['vol_hist']}% a.a.\n"
        f"{'═'*30}\n"
        f"⚠️ _Opções têm risco elevado. Gerencie o tamanho._"
    )
    return _enviar_whatsapp(msg)


def enviar_mercado_preditivo(mercados: list) -> bool:
    """Envia os top mercados preditivos do Polymarket"""
    if not mercados:
        return False
    agora = datetime.now().strftime("%d/%m %H:%M")
    linhas = [
        f"{'═'*30}",
        f"🔮 *MERCADO PREDITIVO — Top Oportunidades*",
        f"🕐 {agora}",
        f"{'─'*30}",
    ]
    for m in mercados[:5]:
        vol = f"${float(m['volume_24h']):,.0f}" if m['volume_24h'] else "N/A"
        linhas.append(
            f"❓ {m['pergunta'][:60]}...\n"
            f"   ✅ SIM: {m['preco_sim']} | ❌ NÃO: {m['preco_nao']}\n"
            f"   💧 Vol 24h: {vol}"
        )
    linhas.append(f"{'═'*30}")
    return _enviar_whatsapp("\n".join(linhas))


def enviar_noticias_relevantes(noticias: list) -> bool:
    """Envia resumo de notícias relevantes"""
    if not noticias:
        return False
    agora = datetime.now().strftime("%d/%m %H:%M")
    linhas = [
        f"{'═'*30}",
        f"📰 *NOTÍCIAS RELEVANTES* — {agora}",
        f"{'─'*30}",
    ]
    for n in noticias[:5]:
        linhas.append(f"[{n['fonte']}] {n['titulo']}")
    linhas.append(f"{'═'*30}")
    return _enviar_whatsapp("\n".join(linhas))


def enviar_resumo_diario(resultados: list) -> bool:
    """Envia resumo do dia com todas as calls emitidas"""
    agora = datetime.now().strftime("%d/%m/%Y")
    calls_compra = [r for r in resultados if r.get("direcao") == "COMPRA"]
    calls_venda  = [r for r in resultados if r.get("direcao") == "VENDA/SHORT"]

    linhas = [
        f"{'═'*30}",
        f"📋 *RESUMO DO DIA — {agora}*",
        f"{'─'*30}",
        f"🟢 Calls de COMPRA: {len(calls_compra)}",
        f"🔴 Calls de VENDA:  {len(calls_venda)}",
        f"{'─'*30}",
        f"🏆 *Melhores setups do dia:*",
    ]
    top = sorted(resultados, key=lambda x: x.get("score", 0), reverse=True)[:5]
    for r in top:
        linhas.append(f"  {EMOJI_DIRECAO.get(r['direcao'],'')} {r['ticker']} — Score {r['score']}")
    linhas.append(f"{'═'*30}")
    linhas.append("Bons trades! 🚀")
    return _enviar_whatsapp("\n".join(linhas))


def enviar_teste() -> bool:
    """Testa se a configuração do WhatsApp está funcionando"""
    msg = (
        "✅ *Sistema de Calls Ativo!*\n"
        "Seu sistema de análise de investimentos foi configurado com sucesso.\n"
        "🟢 WhatsApp conectado\n"
        "📊 Análises de mercado iniciadas\n\n"
        "_Você receberá as calls aqui._"
    )
    return _enviar_whatsapp(msg)
