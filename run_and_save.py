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

portfolio_path = "/root/trading/portfolio.json"
portfolio = json.load(open(portfolio_path))

s_tqqq = float(portfolio["shares_tqqq"])
b_tqqq = float(portfolio["buy_price_tqqq"])
s_agg  = float(portfolio["shares_agg"])
b_agg  = float(portfolio["buy_price_agg"])
s_ibit = float(portfolio.get("shares_ibit", 0))
b_ibit = float(portfolio.get("buy_price_ibit", 0))
q_base = float(portfolio.get("quarter_baseline_price_tqqq", b_tqqq))

# ── Fetch prices ──────────────────────────────────────────────
tickers   = ["TQQQ", "AGG", "IBIT"]
hist_data = yf.download(tickers, period="1y", auto_adjust=False, progress=False)["Close"].dropna()

curr_tqqq = float(hist_data["TQQQ"].iloc[-1])
curr_agg  = float(hist_data["AGG"].iloc[-1])
curr_ibit = float(hist_data["IBIT"].iloc[-1])

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

# ── Portfolio totals ──────────────────────────────────────────
total_buy_val  = buy_val_tqqq  + buy_val_agg  + buy_val_ibit
total_curr_val = curr_val_tqqq + curr_val_agg + curr_val_ibit
total_profit   = total_curr_val - total_buy_val
total_return   = safe(total_profit, total_buy_val)

alloc_tqqq = safe(curr_val_tqqq, total_curr_val)
alloc_agg  = safe(curr_val_agg,  total_curr_val)
alloc_ibit = safe(curr_val_ibit, total_curr_val)

# ── Risk metrics (full portfolio history) ─────────────────────
history   = (s_tqqq * hist_data["TQQQ"]) + (s_agg * hist_data["AGG"]) + (s_ibit * hist_data["IBIT"])
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

💰 *Total Value:* `${total_curr_val:,.2f}`
📈 *Total Return:* `{f(total_return)*100:+.2f}%` (${total_profit:,.2f})

🔹 *TQQQ:* ${curr_tqqq:,.2f} ({f(return_tqqq)*100:+.2f}%)
🔹 *AGG:* ${curr_agg:,.2f} ({f(return_agg)*100:+.2f}%)
🔹 *IBIT:* ${curr_ibit:,.2f} ({f(return_ibit)*100:+.2f}%)

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
