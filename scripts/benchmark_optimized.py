
import csv
import getpass
import statistics
import time
from datetime import datetime
from pathlib import Path

import mysql.connector


QUERIES = {
    "Q1: Delivered orders in October 2025": """
        SELECT COUNT(*)
        FROM orders
        WHERE status = 'DELIVERED'
          AND order_date >= '2025-10-01'
          AND order_date < '2025-11-01'
    """,
    "Q2: Electronics products priced 100-1000": """
        SELECT COUNT(*)
        FROM products
        WHERE category = 'Electronics'
          AND price BETWEEN 100 AND 1000
    """,
    "Q3: Monthly order count and total for June 2025": """
        SELECT COUNT(*), SUM(total_amount)
        FROM orders
        WHERE order_date >= '2025-06-01'
          AND order_date < '2025-07-01'
    """,
}

REPEATS = 7
OUTPUT_FILE = Path("benchmarks/optimized_benchmark.csv")


def main():
    password = getpass.getpass("Enter MySQL root password: ")

    connection = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password=password,
        database="high_performance_db",
        connection_timeout=10,
    )

    try:
        cursor = connection.cursor()
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        file_exists = OUTPUT_FILE.exists() and OUTPUT_FILE.stat().st_size > 0

        with OUTPUT_FILE.open("a", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "timestamp",
                "query",
                "runs",
                "result",
                "minimum_ms",
                "median_ms",
                "maximum_ms",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            print("\nINDEXED QUERY BENCHMARK")
            print(f"Measured runs per query: {REPEATS}")
            print(f"CSV output: {OUTPUT_FILE}\n")

            for name, query in QUERIES.items():
                cursor.execute(query)
                expected_result = cursor.fetchall()
                timings = []

                for _ in range(REPEATS):
                    start = time.perf_counter()
                    cursor.execute(query)
                    result = cursor.fetchall()
                    elapsed_ms = (time.perf_counter() - start) * 1000
                    timings.append(elapsed_ms)

                    if result != expected_result:
                        raise RuntimeError(
                            f"Unexpected result change for {name}"
                        )

                minimum = min(timings)
                median = statistics.median(timings)
                maximum = max(timings)

                print(name)
                print(f"  Result: {expected_result}")
                print(f"  Minimum: {minimum:.3f} ms")
                print(f"  Median:  {median:.3f} ms")
                print(f"  Maximum: {maximum:.3f} ms\n")

                writer.writerow({
                    "timestamp": datetime.now().astimezone().isoformat(
                        timespec="seconds"
                    ),
                    "query": name,
                    "runs": REPEATS,
                    "result": repr(expected_result),
                    "minimum_ms": f"{minimum:.3f}",
                    "median_ms": f"{median:.3f}",
                    "maximum_ms": f"{maximum:.3f}",
                })

        cursor.close()
        print(f"Results saved to {OUTPUT_FILE}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()

