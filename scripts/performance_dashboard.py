
import csv
from pathlib import Path

import pandas as pd
import streamlit as st


CSV_FILE = Path("benchmarks/optimized_benchmark.csv")

st.set_page_config(
    page_title="Database Performance Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 High-Performance Database System")
st.subheader("Query Performance Monitoring Dashboard")
st.caption("Monitor SQL query execution times and benchmark history.")

if not CSV_FILE.exists():
    st.error(f"Benchmark file not found: {CSV_FILE}")
    st.info("Run your optimized benchmark script first.")
    st.stop()

try:
    with CSV_FILE.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
except (OSError, csv.Error) as error:
    st.error(f"Could not read benchmark data: {error}")
    st.stop()

if not rows:
    st.warning("No benchmark records are available yet.")
    st.stop()

df = pd.DataFrame(rows)

required_columns = {
    "timestamp",
    "query",
    "runs",
    "result",
    "minimum_ms",
    "median_ms",
    "maximum_ms",
}

if not required_columns.issubset(df.columns):
    st.error("The benchmark CSV does not contain all required columns.")
    st.stop()

for column in ["minimum_ms", "median_ms", "maximum_ms"]:
    df[column] = pd.to_numeric(df[column], errors="coerce")

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["runs"] = pd.to_numeric(df["runs"], errors="coerce")

df = df.dropna(subset=["query", "median_ms", "timestamp"])

if df.empty:
    st.warning("No valid benchmark records were found.")
    st.stop()

st.markdown("### 🔎 Filter queries")

query_names = sorted(df["query"].unique().tolist())

selected_queries = st.multiselect(
    "Select queries",
    options=query_names,
    default=query_names,
)

filtered = df[df["query"].isin(selected_queries)].copy()

if filtered.empty:
    st.info("Select at least one query to view results.")
    st.stop()

latest = (
    filtered.sort_values("timestamp")
    .groupby("query", as_index=False)
    .tail(1)
    .sort_values("query")
)

st.markdown("### 📌 Latest performance summary")

metric1, metric2, metric3 = st.columns(3)

metric1.metric("Queries monitored", len(latest))
metric2.metric(
    "Average median time",
    f"{latest['median_ms'].mean():.3f} ms",
)
metric3.metric(
    "Fastest median time",
    f"{latest['median_ms'].min():.3f} ms",
)

st.markdown("### ⏱️ Median execution time by query")

chart_data = latest.set_index("query")[["median_ms"]]

st.bar_chart(
    chart_data,
    y="median_ms",
    x_label="SQL query",
    y_label="Median execution time (ms)",
    height=400,
)

st.caption("Lower execution time generally means faster execution.")

st.markdown("### 📈 Benchmark history")

if filtered["timestamp"].nunique() < 2:
    st.info(
        "History needs benchmark runs at different timestamps. "
        "Run the benchmark script again later to build a useful trend."
    )
else:
    history = filtered.pivot_table(
        index="timestamp",
        columns="query",
        values="median_ms",
        aggfunc="last",
    ).sort_index()

    st.line_chart(
        history,
        x_label="Benchmark timestamp",
        y_label="Median execution time (ms)",
        height=400,
    )

result_columns = [
    "query",
    "runs",
    "result",
    "minimum_ms",
    "median_ms",
    "maximum_ms",
    "timestamp",
]

st.markdown("### 📋 Latest results for each query")

st.dataframe(
    latest[result_columns].reset_index(drop=True),
    width="stretch",
    hide_index=True,
    column_config={
        "query": st.column_config.TextColumn("SQL Query", width="large"),
        "runs": st.column_config.NumberColumn("Measured Runs"),
        "result": st.column_config.TextColumn("Query Result", width="large"),
        "minimum_ms": st.column_config.NumberColumn(
            "Minimum (ms)", format="%.3f"
        ),
        "median_ms": st.column_config.NumberColumn(
            "Median (ms)", format="%.3f"
        ),
        "maximum_ms": st.column_config.NumberColumn(
            "Maximum (ms)", format="%.3f"
        ),
        "timestamp": st.column_config.DatetimeColumn("Benchmark Time"),
    },
)

st.markdown("### 🗂️ Complete benchmark history")

st.dataframe(
    filtered.sort_values("timestamp", ascending=False).reset_index(drop=True),
    width="stretch",
    hide_index=True,
)

st.download_button(
    label="⬇️ Download filtered benchmark data (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="benchmark_results.csv",
    mime="text/csv",
)

st.divider()

st.caption(
    "Measurements include Python-to-MySQL execution and result-fetch overhead. "
    "Timings vary with caching and system load. Reliable comparisons require "
    "consistent test conditions."
)

