import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).parent / "immunology.db"
CSV_PATH = Path(__file__).parent / "cell-count.csv"


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_csv(CSV_PATH)

    df.to_sql("samples", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()

    print(f"Loaded {len(df)} rows into {DB_PATH.name}")


if __name__ == "__main__":
    main()
