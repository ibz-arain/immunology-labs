import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).parent / "immunology.db"


def main():
    conn = sqlite3.connect(DB_PATH)

    baseline_samples = pd.read_sql_query(
        """
        SELECT *
        FROM samples
        WHERE condition = 'melanoma'
          AND treatment = 'miraclib'
          AND sample_type = 'PBMC'
          AND time_from_treatment_start = 0
    """,
        conn,
    )

    samples_per_project = pd.read_sql_query(
        """
        SELECT project, COUNT(*) AS sample_count
        FROM samples
        WHERE condition = 'melanoma'
          AND treatment = 'miraclib'
          AND sample_type = 'PBMC'
          AND time_from_treatment_start = 0
        GROUP BY project
        ORDER BY project
    """,
        conn,
    )

    subjects_by_response = pd.read_sql_query(
        """
        SELECT response, COUNT(DISTINCT subject) AS subject_count
        FROM samples
        WHERE condition = 'melanoma'
          AND treatment = 'miraclib'
          AND sample_type = 'PBMC'
          AND time_from_treatment_start = 0
        GROUP BY response
        ORDER BY response
    """,
        conn,
    )

    subjects_by_sex = pd.read_sql_query(
        """
        SELECT sex, COUNT(DISTINCT subject) AS subject_count
        FROM samples
        WHERE condition = 'melanoma'
          AND treatment = 'miraclib'
          AND sample_type = 'PBMC'
          AND time_from_treatment_start = 0
        GROUP BY sex
        ORDER BY sex
    """,
        conn,
    )

    conn.close()

    print(
        f"Baseline melanoma PBMC samples treated with miraclib: {len(baseline_samples)}"
    )

    print("\nSamples per project:")
    print(samples_per_project.to_string(index=False))

    print("\nSubjects by response:")
    print(subjects_by_response.to_string(index=False))

    print("\nSubjects by sex:")
    print(subjects_by_sex.to_string(index=False))


if __name__ == "__main__":
    main()
