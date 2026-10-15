
-- EcoDC-style database performance project:
-- Indexes for high-performance order queries.
-- MySQL 9.3

CREATE INDEX idx_orders_status_date
ON orders (status, order_date);

CREATE INDEX idx_orders_order_date
ON orders (order_date);

