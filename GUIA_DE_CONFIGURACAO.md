# 📊 SISTEMA DE CALLS DE INVESTIMENTO
## Guia Completo de Configuração e Uso

---

## 🗂 O que o sistema faz

Você vai receber no seu **WhatsApp**, automaticamente, mensagens como esta:

```
══════════════════════════════
🇧🇷 CALL — PETR4.SA
🟢📈 COMPRA  |  Score: 82/100
🕐 10/02 14:35
──────────────────────────────
💰 Entrada:  R$38.45
🛑 Stop Loss: R$37.20
🎯 Take Profit: R$40.90
📉 RSI: 28.3
──────────────────────────────
📡 Sinais:
  🟢 RSI SAINDO DE SOBREVENDA (28.3)
  🟢 MACD CRUZAMENTO ALTISTA
  🟢 VOLUME SPIKE 2.4x acima da média
══════════════════════════════
```

---

## 📋 PASSO A PASSO DE INSTALAÇÃO

### PASSO 1 — Instalar o Python

1. Acesse: **https://www.python.org/downloads/**
2. Baixe a versão mais recente (3.11 ou superior)
3. Na instalação, marque **"Add Python to PATH"** ✅
4. Clique em "Install Now"

---

### PASSO 2 — Baixar o sistema

1. Coloque a pasta `investment-calls` em um local fácil de achar
   - Sugestão: `C:\Users\SeuNome\investment-calls` (Windows)
   - Sugestão: `~/investment-calls` (Mac/Linux)

---

### PASSO 3 — Instalar as dependências

**Windows:**
1. Abra a pasta `investment-calls`
2. Segure `SHIFT` e clique com botão direito
3. Clique em "Abrir janela do PowerShell aqui"
4. Digite: `pip install -r requirements.txt` e pressione ENTER
5. Aguarde instalar (pode demorar 2-3 minutos)

**Mac/Linux:**
1. Abra o Terminal
2. Navegue até a pasta: `cd ~/investment-calls`
3. Execute: `bash setup.sh`

---

### PASSO 4 — Configurar o WhatsApp (CallMeBot)

O **CallMeBot** é gratuito e envia mensagens direto no seu WhatsApp.

**Como ativar (1 minuto):**

1. Salve o número **+34 644 60 49 48** na sua agenda com o nome "CallMeBot"
2. Mande a seguinte mensagem para este número no WhatsApp:
   ```
   I allow callmebot to send me messages
   ```
3. Você receberá um número de **API KEY** em resposta (ex: `1234567`)
4. Guarde esse número

> ⚠️ Se não responder em 2 minutos, tente novamente. O serviço às vezes demora.

---

### PASSO 5 — Editar o arquivo config.py

Abra o arquivo `config.py` (com o Bloco de Notas ou qualquer editor).

**Altere apenas estas 2 linhas:**

```python
WHATSAPP_NUMBER = "+5511988887777"   # ← SEU número com DDI
CALLMEBOT_APIKEY = "1234567"         # ← SUA API KEY recebida no Zap
```

> 💡 **Dica:** O número deve estar no formato +55 + DDD + número (sem espaços)
> Exemplo: +5521987654321

---

### PASSO 6 — Testar o sistema

No terminal/PowerShell, dentro da pasta do sistema, execute:

```bash
python main.py --teste
```

Se tudo estiver certo, você receberá uma mensagem no WhatsApp:
> ✅ *Sistema de Calls Ativo!*

---

### PASSO 7 — Iniciar o sistema

```bash
python main.py
```

O sistema irá:
- 🔍 Analisar todos os ativos configurados
- 📊 Calcular os indicadores técnicos
- 📱 Enviar calls automaticamente no WhatsApp

---

## 🔧 PERSONALIZAÇÕES IMPORTANTES no config.py

### Quais ativos monitorar?
Edite as listas no `config.py`:
```python
ACOES_BR = ["PETR4.SA", "VALE3.SA", ...]   # Ações da B3
ACOES_EUA = ["AAPL", "TSLA", "NVDA", ...]  # Ações nos EUA
CRIPTOS = ["BTC/USDT", "ETH/USDT", ...]    # Criptomoedas
```

### Horário de análise:
```python
HORARIO_INICIO = "09:00"   # Começa às 9h
HORARIO_FIM    = "18:00"   # Para às 18h
```

### Frequência de análise:
```python
INTERVALO_MINUTOS = 15   # Analisa a cada 15 minutos
```

### Sensibilidade das calls (score mínimo):
```python
SCORE_MINIMO_CALL = 65   # 0-100. Mais alto = menos calls, mais precisas
```

---

## 🏦 CORRETORAS RECOMENDADAS

| Mercado | Corretora | Por quê? |
|---------|-----------|----------|
| Ações/Opções/FIIs BR | **XP Investimentos** | Maior plataforma BR, tem API |
| Ações/Opções/FIIs BR | **Clear Corretora** | Zero taxa Day Trade |
| Futuros B3 (WIN/WDO) | **Rico** ou **Genial** | Acesso direto ao mini |
| Ações EUA + ETFs | **Avenue** | Conta em dólar, intuitiva |
| Cripto | **Binance** | Maior liquidez, melhor API |
| Cripto BR | **Mercado Bitcoin** | Para depósito em reais |
| Mercado Preditivo | **Polymarket** | Requer MetaMask + USDC |

---

## 📈 INDICADORES UTILIZADOS

| Indicador | O que faz |
|-----------|-----------|
| **RSI** | Mede força da tendência. <30 = sobrevendido (comprar), >70 = sobrecomprado (vender) |
| **MACD** | Cruzamento das médias móveis. Sinal de entrada/saída de tendência |
| **Bollinger Bands** | Preço tocando a banda = possível reversão |
| **EMA 9/21/50** | Alinhamento das médias = tendência confirmada |
| **Volume** | Spike de volume confirma a força do movimento |
| **ATR** | Calcula stop e take profit automaticamente |
| **Divergência** | Preço e RSI indo em direções opostas = reversão iminente |

---

## 🖥 COMO MANTER O SISTEMA RODANDO 24/7

### Opção 1 — Computador pessoal (mais simples)
Deixe o terminal aberto com o sistema rodando.

### Opção 2 — Servidor na nuvem (recomendado)
Use uma VM gratuita no **Oracle Cloud Free Tier**:
1. Acesse: https://www.oracle.com/cloud/free/
2. Crie uma VM Ubuntu gratuita
3. Copie os arquivos para o servidor
4. Execute com: `nohup python3 main.py &`

### Opção 3 — Google Colab (grátis, para testes)
Abra o Google Colab e execute as células com o código.

---

## ❓ PERGUNTAS FREQUENTES

**Q: O sistema compra automaticamente?**
> Não. O sistema apenas envia ALERTAS. A decisão de comprar ou vender é sempre sua.

**Q: O sistema é garantia de lucro?**
> Não. Nenhum sistema de análise técnica garante lucro. Use sempre stop loss e gerencie seu risco.

**Q: Posso adicionar mais ativos?**
> Sim! Basta adicionar os tickers nas listas do `config.py`.

**Q: Como encontro o ticker de uma ação?**
> Yahoo Finance: https://finance.yahoo.com — busque o nome da empresa e copie o símbolo.
> Ações BR sempre têm `.SA` no final (ex: PETR4.SA).

**Q: O sistema analisa gráficos?**
> Sim, via indicadores técnicos calculados sobre os dados OHLCV (Abertura, Máxima, Mínima, Fechamento, Volume).

---

## ⚠️ AVISO LEGAL

Este sistema é uma ferramenta de **auxílio à análise técnica** e **não constitui recomendação de investimento**.
Investimentos envolvem riscos. Nunca invista mais do que você pode perder.
O autor não se responsabiliza por perdas financeiras decorrentes do uso deste sistema.

---

*Sistema desenvolvido com Python 3.11 + yfinance + ccxt + CallMeBot*
