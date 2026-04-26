import sqlite3
import os

DB_PATH = "/root/trading/trading.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create table if it doesn't exist
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
    conn.commit()
    conn.close()

def insert_run(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    sql = f'INSERT INTO runs ({columns}) VALUES ({placeholders})'
    
    c.execute(sql, list(data.values()))
    conn.commit()
    conn.close()
