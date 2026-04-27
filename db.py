import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "trading.db"))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at TEXT,
            price_tqqq REAL,
            price_agg REAL,
            shares_tqqq REAL,
            shares_agg REAL,
            buy_price_tqqq REAL,
            buy_price_agg REAL,
            buy_val_tqqq REAL,
            curr_val_tqqq REAL,
            profit_tqqq REAL,
            return_tqqq REAL,
            buy_val_agg REAL,
            curr_val_agg REAL,
            profit_agg REAL,
            return_agg REAL,
            total_buy_val REAL,
            total_curr_val REAL,
            total_profit REAL,
            total_return REAL,
            alloc_tqqq REAL,
            alloc_agg REAL,
            ann_return REAL,
            volatility REAL,
            sharpe REAL,
            max_drawdown REAL,
            quarter_baseline_price REAL,
            quarter_start_value REAL,
            quarter_target_value REAL,
            quarter_perf REAL,
            quarter_gap REAL,
            quarter_action TEXT,
            shares_to_trade REAL
        )
    ''')

    # Migrate: add IBIT columns if not present
    existing = {row[1] for row in c.execute("PRAGMA table_info(runs)").fetchall()}
    new_cols = {
        "price_ibit":        "REAL",
        "shares_ibit":       "REAL",
        "buy_price_ibit":    "REAL",
        "buy_val_ibit":      "REAL",
        "curr_val_ibit":     "REAL",
        "profit_ibit":       "REAL",
        "return_ibit":       "REAL",
        "alloc_ibit":        "REAL",
        "price_adc":         "REAL",
        "shares_adc":        "REAL",
        "buy_price_adc":     "REAL",
        "buy_val_adc":       "REAL",
        "curr_val_adc":      "REAL",
        "profit_adc":        "REAL",
        "return_adc":        "REAL",
        "alloc_adc":         "REAL",
        "aed_usd_rate":      "REAL",
        "curr_val_adc_usd":  "REAL",
        "buy_val_adc_usd":   "REAL",
        "daily_change":      "REAL",
        "daily_change_pct":  "REAL",
    }
    for col, typ in new_cols.items():
        if col not in existing:
            c.execute(f"ALTER TABLE runs ADD COLUMN {col} {typ}")

    conn.commit()
    conn.close()

def insert_run(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    c.execute(f'INSERT INTO runs ({columns}) VALUES ({placeholders})', list(data.values()))
    conn.commit()
    conn.close()
