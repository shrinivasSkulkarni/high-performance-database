import getpass
import random
from datetime import datetime, timedelta
from decimal import Decimal
from itertools import product as cartesian_product

import mysql.connector
from mysql.connector import Error


# Reproducible benchmark configuration
CUSTOMER_COUNT = 10_000
PRODUCT_COUNT = 1_000
ORDER_COUNT = 50_000
ITEMS_PER_ORDER = 3
BATCH_SIZE = 2_000
SEED = 42

random.seed(SEED)

FIRST_NAMES = [
    "Aarav", "Isha", "Rohan", "Anaya", "Arjun",
    "Meera", "Kabir", "Diya", "Vihaan", "Sara",
    "Aditya", "Neha", "Rahul", "Priya", "Karan",
]
LAST_NAMES = [
    "Sharma", "Patel", "Kulkarni", "Deshmukh",
    "Joshi", "Singh", "Verma", "Shah", "Rao",
    "Gupta", "Khan", "Mehta", "Pawar", "Nair",
]
CATEGORIES = [
    "Electronics", "Books", "Clothing", "Home",
    "Sports", "Accessories", "Toys", "Kitchen",
]
STATUSES = [
    "PENDING", "PROCESSING", "SHIPPED",
    "DELIVERED", "CANCELLED",
]
PAYMENT_METHODS = ["CARD", "UPI", "NET_BANKING", "COD"]


def batches(rows, size=BATCH_SIZE):
    for start in range(0, len(rows), size):
        yield rows[start:start + size]


def insert_many(cursor, statement, rows):
    total = 0
    for batch in batches(rows):
        cursor.executemany(statement, batch)
        total += len(batch)
    return total


def main():
    password = getpass.getpass("Enter MySQL root password: ")

    connection = None

    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password=password,
            database="high_performance_db",
            connection_timeout=10,
        )

        cursor = connection.cursor()

        # Safety check: never append or overwrite existing benchmark data.
        tables = [
            "customers", "products", "orders",
            "order_items", "payments",
        ]

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            if count:
                raise RuntimeError(
                    f"Table '{table}' already contains {count} rows. "
                    "No data was intentionally added. Inspect the database "
                    "before deciding how to proceed."
                )

        rng = random.Random(SEED)
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2026, 1, 1)
        seconds_in_period = int((end_date - start_date).total_seconds())

        # 1. Generate customers.
        name_pairs = list(cartesian_product(FIRST_NAMES, LAST_NAMES))
        customers = []

        for customer_id in range(1, CUSTOMER_COUNT + 1):
            first, last = name_pairs[(customer_id - 1) % len(name_pairs)]
            customers.append((
                customer_id,
                f"{first} {last} {customer_id}",
                f"customer{customer_id}@example.com",
                rng.choice([
                    "Pune", "Mumbai", "Nashik", "Bengaluru",
                    "Delhi", "Hyderabad", "Chennai", "Jaipur",
                ]),
                start_date + timedelta(
                    seconds=rng.randrange(seconds_in_period)
                ),
            ))

        # 2. Generate products and prices in whole cents.
        products = []
        product_prices = {}

        for product_id in range(1, PRODUCT_COUNT + 1):
            price_cents = rng.randint(500, 200_000)
            product_prices[product_id] = price_cents
            products.append((
                product_id,
                f"Product {product_id:04d}",
                rng.choice(CATEGORIES),
                Decimal(price_cents) / 100,
                rng.randint(0, 500),
                start_date,
            ))

        print("Inserting customers and products...")

        insert_many(
            cursor,
            """INSERT INTO customers
               (customer_id, full_name, email, city, created_at)
               VALUES (%s, %s, %s, %s, %s)""",
            customers,
        )

        insert_many(
            cursor,
            """INSERT INTO products
               (product_id, product_name, category, price,
                stock_quantity, created_at)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            products,
        )

        # 3. Generate orders, items, and matching payment amounts.
        orders = []
        items = []
        payments = []

        for order_id in range(1, ORDER_COUNT + 1):
            order_date = start_date + timedelta(
                seconds=rng.randrange(seconds_in_period)
            )
            customer_id = rng.randint(1, CUSTOMER_COUNT)
            status = rng.choice(STATUSES)
            total_cents = 0

            selected_products = rng.sample(
                range(1, PRODUCT_COUNT + 1),
                ITEMS_PER_ORDER,
            )

            order_items = []
            for product_id in selected_products:
                quantity = rng.randint(1, 5)
                unit_price_cents = product_prices[product_id]
                total_cents += quantity * unit_price_cents

                order_items.append((
                    order_id,
                    product_id,
                    quantity,
                    Decimal(unit_price_cents) / 100,
                ))

            orders.append((
                order_id,
                customer_id,
                order_date,
                status,
                Decimal(total_cents) / 100,
            ))
            items.extend(order_items)

            payment_status = rng.choices(
                ["SUCCESS", "PENDING", "FAILED", "REFUNDED"],
                weights=[80, 10, 8, 2],
                k=1,
            )[0]

            paid_at = (
                order_date + timedelta(minutes=rng.randint(1, 180))
                if payment_status in ("SUCCESS", "REFUNDED")
                else None
            )

            payments.append((
                order_id,
                order_id,
                rng.choice(PAYMENT_METHODS),
                Decimal(total_cents) / 100,
                payment_status,
                paid_at,
            ))

        print("Inserting orders and order items...")

        insert_many(
            cursor,
            """INSERT INTO orders
               (order_id, customer_id, order_date, status, total_amount)
               VALUES (%s, %s, %s, %s, %s)""",
            orders,
        )

        insert_many(
            cursor,
            """INSERT INTO order_items
               (order_id, product_id, quantity, unit_price)
               VALUES (%s, %s, %s, %s)""",
            items,
        )

        insert_many(
            cursor,
            """INSERT INTO payments
               (payment_id, order_id, payment_method, amount,
                payment_status, paid_at)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            payments,
        )

        # All generated rows are committed together.
        connection.commit()
        print("\nBenchmark data generated successfully.")

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            print(f"{table}: {cursor.fetchone()[0]:,} rows")

        cursor.close()

    except (Error, RuntimeError, ValueError) as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        print(f"\nData generation failed: {error}")
        print("The current transaction was rolled back where possible.")

    finally:
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()
