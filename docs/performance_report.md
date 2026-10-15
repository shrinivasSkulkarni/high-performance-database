# High-Performance Database System
## Database Performance Optimization Report

### 1. Project Overview

This project demonstrates database performance optimization using MySQL 9.3. A sample e-commerce database was populated with 261,000 records across five tables.

### 2. Database Tables

| Table | Records |
|---|---:|
| customers | 10,000 |
| products | 1,000 |
| orders | 50,000 |
| order_items | 150,000 |
| payments | 50,000 |
| **Total** | **261,000** |

### 3. Optimization Approach

The initial `EXPLAIN ANALYZE` results showed full table scans for queries filtering the `orders` table. Two indexes were introduced:

- `idx_orders_status_date` on `(status, order_date)`
- `idx_orders_order_date` on `(order_date)`

Subsequent execution plans confirmed that MySQL used index range scans for both queries.

### 4. Benchmark Results

Median execution times from the initial baseline and the latest post-indexing benchmark:

| Query | Before | After | Change |
|---|---:|---:|---:|
| Orders by status and date | 8.629 ms | 1.076 ms | 87.5% faster |
| Products by category and price | 0.283 ms | 0.534 ms | 88.7% slower |
| Monthly order aggregation | 5.448 ms | 4.703 ms | 13.7% faster |

The product query did not receive a new index. Its small timing difference may reflect system load, caching, or measurement overhead and should not be interpreted as an indexing regression.

### 5. Query Execution Plan Findings

**Orders by status and date:** MySQL changed from scanning 50,000 rows to a covering index range scan returning 903 matching rows. The observed `EXPLAIN ANALYZE` execution time decreased from 18.5 ms to 1.29 ms.

**Monthly order aggregation:** MySQL changed from scanning 50,000 rows to an index range scan returning 4,062 matching rows. The observed `EXPLAIN ANALYZE` execution time decreased from 18.3 ms to 8.64 ms.

### 6. Conclusion

The indexing experiment demonstrated that suitable indexes can reduce the number of rows examined and improve query response times. The largest benchmark improvement occurred in the order status and date query.

Further work should include repeatable benchmark runs, testing under concurrent workloads, evaluating index storage overhead, and analyzing additional query patterns.

### 7. Reproducibility Notes

- Database: MySQL 9.3.0
- Dataset: Synthetic test data
- Benchmark: Seven measured runs per query
- Performance results depend on hardware, caching, database state, and system activity.
- The reported times are observations from this test environment, not universal performance guarantees.
