import sqlite3
import pandas as pd

import shutil
from datetime import datetime
import os


DB_PATH = "fundamentals.db"


def reset_database(db_path=DB_PATH, backup=True):
    """
    Safely resets the fundamentals database.
    - Backs up the current DB (optional)
    - Drops all main tables so fresh data can be inserted
    """
    if backup and os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path.replace('.db','')}_backup_{timestamp}.db"
        shutil.copyfile(db_path, backup_path)
        print(f"Database backed up as {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    tables = ["income_statement", "balance_sheet", "cash_flow", "ratios", "scores", "missing_data", "metadata"]
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table}")
    
    conn.commit()
    conn.close()
    print("Database reset completed. Ready for fresh data.")


def get_connection():
    return sqlite3.connect(DB_PATH)

def load_scores():
    conn = get_connection()

    try:
        df = pd.read_sql(
            "SELECT symbol, sector, score FROM scores", 
            conn
        )
    except Exception:
        df = pd.DataFrame(columns=["symbol", "sector", "score"])
    finally:
        conn.close()
    
    return df

def load_last_update():
    conn = get_connection()

    try:
        last_update_df = pd.read_sql(
            "SELECT value FROM metadata WHERE key='last_update'",
            conn
        )
        if not last_update_df.empty:
            last_update = last_update_df["value"].iloc[0]
        else:
            last_update = "Never"
    except Exception:
        last_update = "Never"
    finally:
        conn.close()
    
    return last_update
