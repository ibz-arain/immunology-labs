import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import mannwhitneyu

DB_PATH = Path(__file__).parent / "immunology.db"


def main():
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        """
        SELECT *
        FROM samples
        WHERE condition = 'melanoma'
          AND treatment = 'miraclib'
          AND sample_type = 'PBMC'
          AND response IN ('yes', 'no')
    """,
        conn,
    )

    conn.close()

    populations = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]

    df["total_count"] = df[populations].sum(axis=1)

    rows = []
    for _, row in df.iterrows():
        for population in populations:
            rows.append(
                {
                    "population": population,
                    "response": row["response"],
                    "percentage": (row[population] / row["total_count"]) * 100,
                }
            )

    summary = pd.DataFrame(rows)

    # Boxplot
    sns.boxplot(data=summary, x="population", y="percentage", hue="response")
    plt.title("Cell Population Frequencies: Responders vs Non-responders")
    plt.xlabel("Cell population")
    plt.ylabel("Relative frequency (%)")
    plt.tight_layout()

    plt.savefig("boxplot.png")
    plt.close()

    # Statistical tests
    print("Mann-Whitney U test results")
    print("-" * 40)

    for population in populations:
        responders = summary[
            (summary["population"] == population) & (summary["response"] == "yes")
        ]["percentage"]

        non_responders = summary[
            (summary["population"] == population) & (summary["response"] == "no")
        ]["percentage"]

        result = mannwhitneyu(responders, non_responders, alternative="two-sided")

        significant = result.pvalue < 0.05

        print(
            f"{population}: "
            f"U={result.statistic:.2f}, "
            f"p={result.pvalue:.6f}, "
            f"significant={significant}"
        )


if __name__ == "__main__":
    main()
