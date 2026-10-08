import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent / "immunology.db"


def main():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM samples", conn)
    conn.close()

    populations = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
    df["total_count"] = df[populations].sum(axis=1)

    rows = []
    for _, row in df.iterrows():
        for pop in populations:
            pct = (row[pop] / row["total_count"]) * 100
            rows.append(
                {
                    "sample": row["sample"],
                    "total_count": row["total_count"],
                    "population": pop,
                    "count": row[pop],
                    "percentage": pct,
                }
            )

    summary = pd.DataFrame(rows)
    print(summary)


if __name__ == "__main__":
    main()
