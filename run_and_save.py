import sys
import os
import importlib.util
import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf
import json
import requests
from db import init_db, insert_run

def send_telegram_message(message):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("⚠️ Telegram credentials not found in environment variables.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("🚀 Telegram message sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")

# ── Load optional portfolio_analysis module ───────────────────
try:
    spec = importlib.util.spec_from_file_location(
        "portfolio_analysis",
        "/root/trading/portfolio_analysis.py"
    )
    pa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pa)
    print("Running portfolio analysis module...")
    report = pa.main()
except Exception as e:
    print(f"Note: Could not load portfolio_analysis.py: {e}")

# ── Read portfolio config ─────────────────────────────────────
print("\nProcessing portfolio data...")

portfolio_path = os.getenv("PORTFOLIO_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "portfolio.json"))
portfolio = json.load(open(portfolio_path))

s_tqqq = float(portfolio["shares_tqqq"])
b_tqqq = float(portfolio["buy_price_tqqq"])
s_agg  = float(portfolio["shares_agg"])
b_agg  = float(portfolio["buy_price_agg"])
s_ibit = float(portfolio.get("shares_ibit", 0))
b_ibit = float(portfolio.get("buy_price_ibit", 0))
s_adc  = float(portfolio.get("shares_adc", 0))
b_adc  = float(portfolio.get("buy_price_adc", 0))
q_base = float(portfolio.get("quarter_baseline_price_tqqq", b_tqqq))

# ── Fetch prices ──────────────────────────────────────────────
tickers   = ["TQQQ", "AGG", "IBIT"]
hist_data = yf.download(tickers, period="1y", auto_adjust=False, progress=False)["Close"].dropna()

curr_tqqq = float(hist_data["TQQQ"].iloc[-1])
curr_agg  = float(hist_data["AGG"].iloc[-1])
curr_ibit = float(hist_data["IBIT"].iloc[-1])

# ── Fetch USD/AED rate (AED is pegged at ~3.6725 per USD) ─────
aed_usd_rate = 3.6725
try:
    fx_raw = yf.download("USDAED=X", period="5d", auto_adjust=False, progress=False)["Close"]
    if not fx_raw.empty:
        aed_usd_rate = float(fx_raw.squeeze().iloc[-1])
except Exception as e:
    print(f"⚠️ Could not fetch AED/USD rate, using fixed peg 3.6725: {e}")

# ── Fetch ADCB live price from stockanalysis.com ──────────────
def fetch_adcb_web():
    try:
        import re as _re
        hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get("https://stockanalysis.com/quote/adx/ADCB/", headers=hdrs, timeout=10)
        m = _re.search(r'pd:([\d.]+)', resp.text)
        if m:
            return float(m.group(1))
    except Exception as e:
        print(f"⚠️ Web price fetch failed: {e}")
    return None

curr_adc     = b_adc  # fallback to buy price
adc_hist_usd = None
try:
    adc_raw = yf.download("ADCB.AB", period="1y", auto_adjust=False, progress=False)["Close"]
    if not adc_raw.empty:
        adc_series = adc_raw.squeeze()
        curr_adc = float(adc_series.iloc[-1])
        adc_hist_usd = (s_adc * adc_series / aed_usd_rate).reindex(hist_data.index).ffill().dropna()
        print(f"✅ ADCB.AB price (Yahoo): {curr_adc:.3f} AED")
    else:
        print("⚠️ No ADCB.AB data from Yahoo Finance.")
except Exception as e:
    print(f"⚠️ Yahoo Finance error: {e}")

# ── Try live web price — overrides stale Yahoo data ───────────
web_price = fetch_adcb_web()
if web_price is not None:
    curr_adc = web_price
    print(f"✅ ADCB live price (web): {curr_adc:.3f} AED")

def safe(n, d):
    if d is None or (isinstance(d, float) and abs(d) < 1e-12):
        return np.nan
    return n / d

# ── TQQQ metrics ─────────────────────────────────────────────
buy_val_tqqq  = s_tqqq * b_tqqq
curr_val_tqqq = s_tqqq * curr_tqqq
profit_tqqq   = curr_val_tqqq - buy_val_tqqq
return_tqqq   = safe(profit_tqqq, buy_val_tqqq)

# ── AGG metrics ───────────────────────────────────────────────
buy_val_agg   = s_agg * b_agg
curr_val_agg  = s_agg * curr_agg
profit_agg    = curr_val_agg - buy_val_agg
return_agg    = safe(profit_agg, buy_val_agg)

# ── IBIT metrics ──────────────────────────────────────────────
buy_val_ibit  = s_ibit * b_ibit
curr_val_ibit = s_ibit * curr_ibit
profit_ibit   = curr_val_ibit - buy_val_ibit
return_ibit   = safe(profit_ibit, buy_val_ibit)

# ── ADC metrics (values in AED, USD equiv for totals) ─────────
buy_val_adc      = s_adc * b_adc           # AED
curr_val_adc     = s_adc * curr_adc        # AED
profit_adc       = curr_val_adc - buy_val_adc  # AED
return_adc       = safe(profit_adc, buy_val_adc)
buy_val_adc_usd  = buy_val_adc  / aed_usd_rate  # USD
curr_val_adc_usd = curr_val_adc / aed_usd_rate  # USD

# ── Portfolio totals (USD) ────────────────────────────────────
total_buy_val  = buy_val_tqqq  + buy_val_agg  + buy_val_ibit  + buy_val_adc_usd
total_curr_val = curr_val_tqqq + curr_val_agg + curr_val_ibit + curr_val_adc_usd
total_profit   = total_curr_val - total_buy_val
total_return   = safe(total_profit, total_buy_val)

alloc_tqqq = safe(curr_val_tqqq,    total_curr_val)
alloc_agg  = safe(curr_val_agg,     total_curr_val)
alloc_ibit = safe(curr_val_ibit,    total_curr_val)
alloc_adc  = safe(curr_val_adc_usd, total_curr_val)

# ── Risk metrics (full portfolio history) ─────────────────────
history = (s_tqqq * hist_data["TQQQ"]) + (s_agg * hist_data["AGG"]) + (s_ibit * hist_data["IBIT"])
if adc_hist_usd is not None and not adc_hist_usd.empty:
    history = history.add(adc_hist_usd, fill_value=0)
daily_ret = history.pct_change().dropna()
ann_ret   = float(daily_ret.mean() * 252)
vol       = float(daily_ret.std() * np.sqrt(252))
sharpe    = safe(ann_ret, vol)

roll_max = history.cummax()
dd       = (history - roll_max) / roll_max
max_dd   = float(dd.min())

# ── Quarterly TQQQ target ─────────────────────────────────────
q_start  = s_tqqq * q_base
q_target = q_start * 1.09
q_gap    = q_target - curr_val_tqqq
q_perf   = safe(curr_val_tqqq - q_start, q_start)
q_shares = safe(abs(q_gap), curr_tqqq)

if   q_gap > 0: q_action = "BUY"
elif q_gap < 0: q_action = "SELL"
else:           q_action = "HOLD"

def f(v):
    if v is None: return None
    try:
        return None if (isinstance(v, float) and np.isnan(v)) else float(v)
    except:
        return None

# ── Daily change vs previous calendar day ────────────────────
import sqlite3 as _sqlite3
daily_change = None
daily_change_pct = None
try:
    _conn = _sqlite3.connect(os.getenv("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "trading.db")))
    today_str = datetime.now().strftime("%Y-%m-%d")
    prev_row = _conn.execute(
        "SELECT total_curr_val FROM runs WHERE date(run_at) < ? ORDER BY run_at DESC LIMIT 1",
        (today_str,)
    ).fetchone()
    _conn.close()
    if prev_row and prev_row[0]:
        prev_val = prev_row[0]
        daily_change = total_curr_val - prev_val
        daily_change_pct = daily_change / prev_val
        print(f"📅 Daily change: ${daily_change:+,.2f} ({daily_change_pct*100:+.2f}%)")
    else:
        print("📅 No previous day data for daily change calculation.")
except Exception as e:
    print(f"⚠️ Could not compute daily change: {e}")

# ── Save to DB ────────────────────────────────────────────────
try:
    init_db()
    insert_run({
        "run_at":                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "price_tqqq":             curr_tqqq,
        "price_agg":              curr_agg,
        "price_ibit":             curr_ibit,
        "shares_tqqq":            s_tqqq,
        "shares_agg":             s_agg,
        "shares_ibit":            s_ibit,
        "buy_price_tqqq":         b_tqqq,
        "buy_price_agg":          b_agg,
        "buy_price_ibit":         b_ibit,
        "buy_val_tqqq":           buy_val_tqqq,
        "curr_val_tqqq":          curr_val_tqqq,
        "profit_tqqq":            profit_tqqq,
        "return_tqqq":            f(return_tqqq),
        "buy_val_agg":            buy_val_agg,
        "curr_val_agg":           curr_val_agg,
        "profit_agg":             profit_agg,
        "return_agg":             f(return_agg),
        "buy_val_ibit":           buy_val_ibit,
        "curr_val_ibit":          curr_val_ibit,
        "profit_ibit":            profit_ibit,
        "return_ibit":            f(return_ibit),
        "total_buy_val":          total_buy_val,
        "total_curr_val":         total_curr_val,
        "total_profit":           total_profit,
        "total_return":           f(total_return),
        "alloc_tqqq":             f(alloc_tqqq),
        "alloc_agg":              f(alloc_agg),
        "alloc_ibit":             f(alloc_ibit),
        "price_adc":              curr_adc,
        "shares_adc":             s_adc,
        "buy_price_adc":          b_adc,
        "buy_val_adc":            buy_val_adc,
        "curr_val_adc":           curr_val_adc,
        "profit_adc":             profit_adc,
        "return_adc":             f(return_adc),
        "alloc_adc":              f(alloc_adc),
        "aed_usd_rate":           aed_usd_rate,
        "curr_val_adc_usd":       curr_val_adc_usd,
        "buy_val_adc_usd":        buy_val_adc_usd,
        "daily_change":           f(daily_change),
        "daily_change_pct":       f(daily_change_pct),
        "ann_return":             ann_ret,
        "volatility":             vol,
        "sharpe":                 f(sharpe),
        "max_drawdown":           max_dd,
        "quarter_baseline_price": q_base,
        "quarter_start_value":    q_start,
        "quarter_target_value":   q_target,
        "quarter_perf":           f(q_perf),
        "quarter_gap":            q_gap,
        "quarter_action":         q_action,
        "shares_to_trade":        f(q_shares),
    })
    print("✅ Results saved to database.")
except Exception as e:
    print(f"❌ Database error: {e}")

# ── Telegram report ───────────────────────────────────────────
tg_report = f"""
📊 *Portfolio Analysis Report*
_{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}_

💰 *Total Value:* `${total_curr_val:,.2f}` USD
📅 *Daily Change:* `{"${:+,.2f} ({:+.2f}%)".format(daily_change, daily_change_pct*100) if daily_change is not None else "N/A"}`
📈 *Total Return:* `{f(total_return)*100:+.2f}%` (${total_profit:,.2f})

🔹 *TQQQ:* ${curr_tqqq:,.2f} ({f(return_tqqq)*100:+.2f}%)
🔹 *AGG:* ${curr_agg:,.2f} ({f(return_agg)*100:+.2f}%)
🔹 *IBIT:* ${curr_ibit:,.2f} ({f(return_ibit)*100:+.2f}%)
🔸 *ADC (ADCB):* AED {curr_adc:,.3f} ({f(return_adc)*100:+.2f}%)
   Value: AED {curr_val_adc:,.2f} ≈ ${curr_val_adc_usd:,.2f} USD
   Rate: 1 USD = {aed_usd_rate:.4f} AED

🎯 *Quarterly Target (9%):*
• Status: `{f(q_perf)*100:+.2f}%`
• Action: *{q_action}* {f(q_shares):.2f} shares of TQQQ
• Gap: `${q_gap:,.2f}`

📉 *Risk Metrics:*
• Max Drawdown: `{max_dd*100:.2f}%`
• Sharpe Ratio: `{f(sharpe):.2f}`
"""

send_telegram_message(tg_report)

print(f"\n✅ Done")
