# Immunology Labs

## Dashboard

[Open dashboard](https://immunology-labs.streamlit.app/)

## Run locally or in GitHub Codespaces

From the repository root, run:

```bash
make setup
make pipeline
make dashboard
```

`make dashboard` starts the dashboard at the local URL shown in the terminal.

- `make pipeline` creates `immunology.db` from `cell-count.csv`.
- The dashboard displays the Part 2–4 analysis results.
