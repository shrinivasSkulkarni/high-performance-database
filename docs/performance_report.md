
# High-Performance Database System
## Database Performance Optimization Report

### 1. Project Overview

This project evaluates MySQL query performance using synthetic e-commerce data and indexing techniques.

- **Database:** MySQL 9.3.0
- **Total rows:** 261,000
- **Customers:** 10,000
- **Products:** 1,000
- **Orders:** 50,000
- **Order items:** 150,000
- **Payments:** 50,000

### 2. Indexes Implemented

| Index | Columns | Purpose |
|---|---|---|
| `idx_orders_status_date` | `status, order_date` | Filters orders by status and date |
| `idx_orders_order_date` | `order_date` | Supports date-range queries |
| `idx_orders_date_total` | `order_date, total_amount` | Covers monthly order count and total aggregation |

The composite index supports queries filtering on both status and date. The date index supports date-range filtering. The covering index includes the date and total amount columns required by the monthly aggregation query, potentially reducing table access.

### 3. Benchmark Results

Times below are median execution measurements in milliseconds, collected using the Python benchmark script with seven measured runs per query.

| Query | Before indexes | Latest measured median | Observed change |
|---|---:|---:|---:|
| Q1: Delivered orders in October 2025 | 8.629 ms | 1.078 ms | 87.5% faster |
| Q2: Electronics products priced 100–1000 | 0.283 ms | 0.692 ms | Slower in this run |
| Q3: Monthly order count and total for June 2025 | 5.448 ms | 1.702 ms | 68.8% faster |

**Important:** These are observed measurements, not guaranteed performance figures. The benchmark includes Python-to-MySQL execution and result-fetch overhead, and timings can vary with caching and system load.

Q2 does not use the new order indexes. Its sub-millisecond timings are particularly sensitive to measurement variability. A product-specific index could be evaluated separately if Q2 performance is important.

### 4. Query Plan Analysis

#### Q1: Filter by status and date

Before indexing, MySQL scanned approximately 50,000 rows.

After adding `idx_orders_status_date`, `EXPLAIN ANALYZE` reported a covering index range scan returning 903 matching rows, with an observed total time of approximately 1.29 ms in that plan run.

#### Q3: Monthly order aggregation

Before indexing, MySQL scanned approximately 50,000 rows.

The date index reduced the work to a range scan of approximately 4,062 matching rows. A subsequent covering index on `(order_date, total_amount)` allowed MySQL to perform a covering index range scan.

In the observed plan runs, the covering-index plan took approximately 2.25 ms compared with approximately 8.73 ms for the earlier date-index plan. These individual plan timings can vary between executions.

### 5. Query Result Validation

The benchmark returned consistent expected results in the recorded runs:

- **Q1:** 903 delivered orders
- **Q2:** 60 matching products
- **Q3:** 4,062 orders with a total amount of 35,257,276.17

The unchanged result counts and total support the conclusion that the indexing changes improved access paths without changing the intended query results.

### 6. Conclusion

The order indexes improved the observed performance of the tested order queries, especially Q1 and Q3. The covering index further reduced the work required for monthly aggregation.

Further work should include repeated controlled benchmarks, product-query index evaluation, and measurement under larger datasets and concurrent workloads.

The current results demonstrate the practical value of query-plan analysis and targeted indexing in MySQL.


### 7. Product Query Index Experiment

#### Q2: Filter products by category and price

The query filters products where `category = 'Electronics'` and `price` is between 100 and 1000.

Before adding a product-specific index, `EXPLAIN ANALYZE` reported a table scan of 1,000 products, with 60 rows matching the filter.

The composite index `idx_products_category_price` was created on `(category, price)`. After adding it, `EXPLAIN ANALYZE` reported a covering index range scan using this index and returning the same 60 matching rows.

- **Index:** `idx_products_category_price`
- **Columns:** `category, price`
- **Observed plan time:** approximately 0.11 ms for the aggregate
- **Result:** 60 matching products

This single plan run suggests the index can reduce the work required for this query. The timing is not directly comparable to the Python benchmark median above because measurement methods differ. Repeated, controlled benchmarks are needed to establish a reliable performance improvement.

### 8. Latest Optimized Benchmark Results

A new benchmark run was performed using `scripts/benchmark_optimized.py` with seven measured executions per query.

| Query | Result | Minimum (ms) | Median (ms) | Maximum (ms) |
|---|---:|---:|---:|---:|
| Q1: Delivered orders in October 2025 | 903 | 0.879 | 1.104 | 1.552 |
| Q2: Electronics products priced 100–1000 | 60 | 0.203 | 0.223 | 0.284 |
| Q3: Monthly order count and total for June 2025 | 4,062 | 1.753 | 1.982 | 2.093 |

**Q3 total order amount:** 35,257,276.17

#### Interpretation

- Q1 returned 903 delivered orders, with a median measured time of 1.104 ms.
- Q2 returned 60 matching products, with a median measured time of 0.223 ms.
- Q3 returned 4,062 orders and a total amount of 35,257,276.17, with a median measured time of 1.982 ms.
- All three queries returned consistent results during the measured runs.

#### Benchmark Limitations

These measurements include Python-to-MySQL execution and result-fetch overhead. Timing may vary with cache state, system load, and database conditions.

The latest results should not be compared directly with earlier medians as proof of improvement unless both benchmark runs use the same methodology and controlled conditions. The initial query execution also serves as the result-validation run in the current optimized benchmark script, so it is not a separate warm-up run.

The recorded results are available in `results/optimized_benchmark.txt`.
