import getpass
import statistics
import time

import mysql.connector


QUERIES = {
    "Q1: Filter orders by status and date": """
        SELECT COUNT(*)
        FROM orders
        WHERE status = 'DELIVERED'
          AND order_date >= '2025-10-01'
          AND order_date <  '2025-11-01'
    """,
    "Q2: Filter products by category and price": """
        SELECT COUNT(*)
        FROM products
        WHERE category = 'Electronics'
          AND price BETWEEN 100 AND 1000
    """,
    "Q3: Aggregate order totals by date": """
        SELECT COUNT(*), SUM(total_amount)
        FROM orders
        WHERE order_date >= '2025-06-01'
          AND order_date <  '2025-07-01'
    """,
}

REPEATS = 7


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
        print("\nBASELINE QUERY BENCHMARK")
        print("Existing indexes are retained; no new indexes are created.")
        print(f"Measured runs per query: {REPEATS}\n")

        for name, query in QUERIES.items():
            # Warm-up run; not included in the measurements.
            cursor.execute(query)
            cursor.fetchall()

            timings = []
            result = None

            for _ in range(REPEATS):
                start = time.perf_counter()
                cursor.execute(query)
                result = cursor.fetchall()
                elapsed_ms = (time.perf_counter() - start) * 1000
                timings.append(elapsed_ms)

            print(name)
            print(f"  Result: {result}")
            print(f"  Minimum: {min(timings):.3f} ms")
            print(f"  Median:  {statistics.median(timings):.3f} ms")
            print(f"  Maximum: {max(timings):.3f} ms\n")

        cursor.close()

    finally:
        connection.close()


if __name__ == "__main__":
    main()
