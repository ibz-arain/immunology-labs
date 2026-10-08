import sqlite3
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
    st.title("Immunology Labs")
    st.write("Immune cell population analysis for clinical trial samples.")

    if not DB_PATH.exists():
        st.error("Database not found. Run `python load_data.py` first.")
        return

    samples = load_samples()
    summary = make_summary(samples)

    st.header("Part 2: Cell population frequencies")

    population = st.selectbox(
        "Select a cell population", ["All populations"] + POPULATIONS
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
    )

    st.header("Part 3: Response analysis")

    response_samples = samples[
        (samples["condition"] == "melanoma")
        & (samples["treatment"] == "miraclib")
        & (samples["sample_type"] == "PBMC")
        & (samples["response"].isin(["yes", "no"]))
    ]

    response_summary = make_summary(response_samples)
    response_summary = response_summary[["population", "response", "percentage"]]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(
        data=response_summary, x="population", y="percentage", hue="response", ax=ax
    )
    ax.set_title("Cell Population Frequencies: Responders vs Non-responders")
    ax.set_xlabel("Cell population")
    ax.set_ylabel("Relative frequency (%)")
    st.pyplot(fig)

    results = []
    for population in POPULATIONS:
        responders = response_summary[
            (response_summary["population"] == population)
            & (response_summary["response"] == "yes")
        ]["percentage"]

        non_responders = response_summary[
            (response_summary["population"] == population)
            & (response_summary["response"] == "no")
        ]["percentage"]

        result = mannwhitneyu(responders, non_responders, alternative="two-sided")

        results.append(
            {
                "population": population,
                "p_value": result.pvalue,
                "significant": result.pvalue < 0.05,
            }
        )

    st.dataframe(pd.DataFrame(results), use_container_width=True)

    st.header("Part 4: Baseline melanoma PBMC samples")

    baseline = samples[
        (samples["condition"] == "melanoma")
        & (samples["treatment"] == "miraclib")
        & (samples["sample_type"] == "PBMC")
        & (samples["time_from_treatment_start"] == 0)
    ]

    st.metric("Baseline samples", len(baseline))

    project_counts = baseline.groupby("project").size().reset_index(name="sample_count")
    response_counts = (
        baseline.groupby("response")["subject"]
        .nunique()
        .reset_index(name="subject_count")
    )
    sex_counts = (
        baseline.groupby("sex")["subject"].nunique().reset_index(name="subject_count")
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Samples by project")
        st.dataframe(project_counts, use_container_width=True)

    with col2:
        st.subheader("Subjects by response")
        st.dataframe(response_counts, use_container_width=True)

    with col3:
        st.subheader("Subjects by sex")
        st.dataframe(sex_counts, use_container_width=True)

    average_b_cells = samples[
        (samples["condition"] == "melanoma")
        & (samples["sex"] == "M")
        & (samples["response"] == "yes")
        & (samples["time_from_treatment_start"] == 0)
    ]["b_cell"].mean()

    st.metric(
        "Average B-cell count: melanoma male responders at baseline",
        f"{average_b_cells:.2f}",
    )


if __name__ == "__main__":
    main()
