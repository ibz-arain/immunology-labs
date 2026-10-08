import sqlite3
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from scipy.stats import mannwhitneyu

DB_PATH = Path(__file__).parent / "immunology.db"
POPULATIONS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]


def load_samples():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM samples", conn)
    conn.close()
    return df


def make_summary(df):
    df = df.copy()
    df["total_count"] = df[POPULATIONS].sum(axis=1)

    rows = []
    for _, row in df.iterrows():
        for population in POPULATIONS:
            rows.append(
                {
                    "sample": row["sample"],
                    "response": row["response"],
                    "total_count": row["total_count"],
                    "population": population,
                    "count": row[population],
                    "percentage": (row[population] / row["total_count"]) * 100,
                }
            )

    return pd.DataFrame(rows)


def main():
    st.set_page_config(page_title="Immunology Labs", layout="wide")

    if not DB_PATH.exists():
        subprocess.run(["python", "load_data.py"], check=True)

    samples = load_samples()
    summary = make_summary(samples)

    left, right = st.columns([3, 2])

    with left:
        response_samples = samples[
            (samples["condition"] == "melanoma")
            & (samples["treatment"] == "miraclib")
            & (samples["sample_type"] == "PBMC")
            & (samples["response"].isin(["yes", "no"]))
        ]

        response_summary = make_summary(response_samples)
        response_summary = response_summary[["population", "response", "percentage"]]

        fig, ax = plt.subplots(figsize=(6.2, 2.8))
        sns.boxplot(
            data=response_summary,
            x="population",
            y="percentage",
            hue="response",
            ax=ax,
        )
        ax.set_title("Responders vs Non-responders")
        ax.set_xlabel("")
        ax.set_ylabel("Relative frequency (%)")
        st.pyplot(fig, use_container_width=False)
        plt.close(fig)

    with right:
        baseline = samples[
            (samples["condition"] == "melanoma")
            & (samples["treatment"] == "miraclib")
            & (samples["sample_type"] == "PBMC")
            & (samples["time_from_treatment_start"] == 0)
        ]

        average_b_cells = samples[
            (samples["condition"] == "melanoma")
            & (samples["sex"] == "M")
            & (samples["response"] == "yes")
            & (samples["time_from_treatment_start"] == 0)
        ]["b_cell"].mean()

        metric1, metric2 = st.columns(2)

        with metric1:
            st.metric("Baseline samples", len(baseline))

        with metric2:
            st.metric("Average B cells", f"{average_b_cells:.2f}")

        project_counts = baseline.groupby("project").size().reset_index(name="samples")

        response_counts = (
            baseline.groupby("response")["subject"]
            .nunique()
            .reset_index(name="subjects")
        )

        sex_counts = (
            baseline.groupby("sex")["subject"].nunique().reset_index(name="subjects")
        )

        st.dataframe(
            project_counts,
            use_container_width=True,
            hide_index=True,
            height=110,
        )

        st.dataframe(
            response_counts,
            use_container_width=True,
            hide_index=True,
            height=110,
        )

        st.dataframe(
            sex_counts,
            use_container_width=True,
            hide_index=True,
            height=110,
        )

    population = st.selectbox(
        "Cell population",
        ["All populations"] + POPULATIONS,
    )

    if population == "All populations":
        displayed_summary = summary
    else:
        displayed_summary = summary[summary["population"] == population]

    st.dataframe(
        displayed_summary[
            ["sample", "total_count", "population", "count", "percentage"]
        ],
        use_container_width=True,
        hide_index=True,
        height=260,
    )


if __name__ == "__main__":
    main()
