
-- High-Performance Database System
-- Index definitions for order-query optimization.
-- MySQL 9.3
--
-- Documentation only: these indexes already exist in the test database.
-- Do not execute this file unchanged against that database.

-- Supports filtering by status and date.
CREATE INDEX idx_orders_status_date
ON orders (status, order_date);

-- Supports filtering orders by date.
CREATE INDEX idx_orders_order_date
ON orders (order_date);

-- Covering index for monthly count and total aggregation.
CREATE INDEX idx_orders_date_total
ON orders (order_date, total_amount);

