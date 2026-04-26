import sqlite3
import os
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
        "SELECT run_at, total_curr_val, total_return, price_tqqq, price_agg, sharpe, max_drawdown "
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
