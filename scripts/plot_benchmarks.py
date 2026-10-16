
import csv
from pathlib import Path

import matplotlib.pyplot as plt


CSV_FILE = Path("benchmarks/optimized_benchmark.csv")
OUTPUT_FILE = Path("results/query_performance.png")


def main():
    queries = []
    median_times = []

    with CSV_FILE.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            queries.append(row["query"])
            median_times.append(float(row["median_ms"]))

    if not queries:
        raise ValueError("No benchmark results found in the CSV file.")

    labels = [query.split(":")[0] for query in queries]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, median_times)

    plt.title("Database Query Performance")
    plt.xlabel("Query")
    plt.ylabel("Median Execution Time (ms)")
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    for bar, value in zip(bars, median_times):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.3f} ms",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUTPUT_FILE, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"Chart saved to: {OUTPUT_FILE}")
    print(f"Queries visualized: {len(queries)}")


if __name__ == "__main__":
    main()

