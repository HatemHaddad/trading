import sqlite3
import os
import numpy as np
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Trading Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "trading.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/api/latest")
def latest():
    conn = get_db()
    row = conn.execute("SELECT * FROM runs ORDER BY run_at DESC LIMIT 1").fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="No data yet")
    return dict(row)


@app.get("/api/history")
def history(limit: int = 90):
    conn = get_db()
    rows = conn.execute(
        "SELECT run_at, total_curr_val, total_return, price_tqqq, price_agg, "
        "price_adc, aed_usd_rate, curr_val_adc, curr_val_adc_usd, sharpe, max_drawdown "
        "FROM runs ORDER BY run_at ASC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/runs")
def runs(limit: int = 50, offset: int = 0):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM runs ORDER BY run_at DESC LIMIT ? OFFSET ?",
        (limit, offset)
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
    conn.close()
    return {"total": total, "runs": [dict(r) for r in rows]}


@app.get("/api/watchlist")
def watchlist():
    raw = yf.download(["SPMO"], period="1y", auto_adjust=False, progress=False)
    if raw.empty:
        raise HTTPException(status_code=503, detail="Could not fetch SPMO data")

    close = raw["Close"]
    spmo = close["SPMO"] if hasattr(close, "columns") and "SPMO" in close.columns else close.squeeze()
    spmo = spmo.dropna()

    if len(spmo) == 0:
        raise HTTPException(status_code=503, detail="No SPMO price data")

    curr = float(spmo.iloc[-1])

    def rel_ret(days):
        if len(spmo) < days + 1:
            return None
        return float((curr - spmo.iloc[-days]) / spmo.iloc[-days])

    daily_ret = spmo.pct_change().dropna()
    vol = float(daily_ret.std() * np.sqrt(252))
    ann_ret = float(daily_ret.mean() * 252)
    sharpe = float(ann_ret / vol) if vol > 1e-9 else None

    roll_max = spmo.cummax()
    max_dd = float(((spmo - roll_max) / roll_max).min())

    ma50 = float(spmo.iloc[-50:].mean()) if len(spmo) >= 50 else None

    return {
        "ticker": "SPMO",
        "name": "Invesco S&P 500 Momentum ETF",
        "curr_price": curr,
        "ret_1m": rel_ret(22),
        "ret_3m": rel_ret(66),
        "ret_6m": rel_ret(132),
        "ret_1y": float((curr - float(spmo.iloc[0])) / float(spmo.iloc[0])),
        "volatility": vol,
        "ann_return": ann_ret,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "ma50": ma50,
        "above_ma50": bool(curr > ma50) if ma50 is not None else None,
    }
