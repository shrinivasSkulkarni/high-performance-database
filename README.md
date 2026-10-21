# High-Performance Database Optimization

A MySQL database performance project focused on improving query execution speed through indexing, benchmarking, and visualization.

## Overview

This project compares SQL query performance before and after applying database indexes to a relational dataset containing 261,000 records across five tables. It includes benchmark scripts, performance charts, and a Streamlit dashboard.

## Technology Stack

- MySQL
- Python
- mysql-connector-python
- pandas
- matplotlib
- Streamlit
- Git and GitHub

## Database Design

**Database:** `high_performance_db`

| Table | Records |
|---|---:|
| customers | 10,000 |
| products | 1,000 |
| orders | 50,000 |
| order_items | 150,000 |
| payments | 50,000 |
| **Total** | **261,000** |

Schema file: `sql/schema.sql`

## Indexing Strategy

The project uses four indexes to improve common query patterns:

- `idx_orders_status_date` — filtering orders by status and date
- `idx_orders_order_date` — querying orders by date
- `idx_orders_date_total` — querying orders by date and total amount
- `idx_products_category_price` — filtering products by category and price

Index definitions: `sql/indexes/orders_indexes.sql`

## Benchmark Results

Median query execution times measured in the local environment:

| Query | Before | After | Improvement |
|---|---:|---:|---:|
| Q1: Orders filtered by status and date | 9.629 ms | 1.437 ms | 85.1% faster |
| Q2: Products filtered by category and price | 0.322 ms | 0.291 ms | 9.6% faster |
| Q3: Monthly order aggregation | 5.824 ms | 2.105 ms | 63.8% faster |

Results may vary depending on hardware, MySQL configuration, data distribution, and workload. Indexes can improve read performance but also increase storage requirements and write overhead.

## Benchmark Artifacts
- Benchmark results: `benchmarks/optimized_benchmark.csv`
- Performance chart: `results/query_performance.png`

## Project Repository

[View this project on GitHub](https://github.com/shrinivasSkulkarni/high-performance-database)
