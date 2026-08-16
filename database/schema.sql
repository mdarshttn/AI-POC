-- Logical Unity Catalog schema for this POC.
-- Tables are created by the PySpark jobs (Delta overwrite), not by running this file.
-- Catalog: workspace. Schemas: bronze, silver, ops, gold.

CREATE SCHEMA IF NOT EXISTS workspace.bronze;
CREATE SCHEMA IF NOT EXISTS workspace.silver;
CREATE SCHEMA IF NOT EXISTS workspace.ops;
CREATE SCHEMA IF NOT EXISTS workspace.gold;

-- Bronze: payload stored as STRING plus ingest metadata.
-- Created by src/bronze/ingest_all.py

CREATE TABLE IF NOT EXISTS workspace.bronze.customers (
  customer_id STRING,
  first_name STRING,
  last_name STRING,
  email STRING,
  signup_date STRING,
  country STRING,
  city STRING,
  _ingest_file STRING,
  _ingest_ts TIMESTAMP,
  _run_id STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS workspace.bronze.products (
  product_id STRING,
  product_name STRING,
  category STRING,
  unit_price STRING,
  in_stock STRING,
  _ingest_file STRING,
  _ingest_ts TIMESTAMP,
  _run_id STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS workspace.bronze.orders (
  order_id STRING,
  customer_id STRING,
  product_id STRING,
  order_date STRING,
  quantity STRING,
  unit_price STRING,
  order_status STRING,
  payment_method STRING,
  _ingest_file STRING,
  _ingest_ts TIMESTAMP,
  _run_id STRING
) USING DELTA;

-- Silver: typed clean rows. Created by src/silver/create_silver_tables.py

CREATE TABLE IF NOT EXISTS workspace.silver.customers (
  customer_id STRING,
  first_name STRING,
  last_name STRING,
  email STRING,
  signup_date DATE,
  country STRING,
  city STRING,
  _ingest_file STRING,
  _ingest_ts TIMESTAMP,
  _bronze_run_id STRING,
  _silver_run_id STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS workspace.silver.products (
  product_id STRING,
  product_name STRING,
  category STRING,
  unit_price DECIMAL(10,2),
  in_stock INT,
  _ingest_file STRING,
  _ingest_ts TIMESTAMP,
  _bronze_run_id STRING,
  _silver_run_id STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS workspace.silver.orders (
  order_id STRING,
  customer_id STRING,
  product_id STRING,
  order_date TIMESTAMP,
  quantity INT,
  unit_price DECIMAL(10,2),
  order_status STRING,
  payment_method STRING,
  _ingest_file STRING,
  _ingest_ts TIMESTAMP,
  _bronze_run_id STRING,
  _silver_run_id STRING
) USING DELTA;

-- Ops: quarantine keeps original Bronze strings plus rule metadata.

CREATE TABLE IF NOT EXISTS workspace.ops.dq_results (
  silver_run_id STRING,
  bronze_run_id STRING,
  table_name STRING,
  rule_id STRING,
  record_id STRING,
  row_fingerprint STRING,
  failed_column STRING,
  failed_value STRING,
  severity STRING,
  message STRING
) USING DELTA;

-- Gold: created by src/gold/create_gold_tables.py

CREATE TABLE IF NOT EXISTS workspace.gold.dim_customer (
  customer_id STRING,
  first_name STRING,
  last_name STRING,
  email STRING,
  signup_date DATE,
  country STRING,
  city STRING,
  _gold_run_id STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS workspace.gold.dim_product (
  product_id STRING,
  product_name STRING,
  category STRING,
  list_unit_price DECIMAL(10,2),
  in_stock INT,
  _gold_run_id STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS workspace.gold.fact_orders (
  order_id STRING,
  customer_id STRING,
  product_id STRING,
  order_date DATE,
  quantity INT,
  unit_price DECIMAL(10,2),
  order_sales DECIMAL(20,2),
  order_status STRING,
  payment_method STRING,
  _gold_run_id STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS workspace.gold.sales_performance (
  total_orders BIGINT,
  total_quantity BIGINT,
  total_sales DECIMAL(20,2),
  average_order_value DECIMAL(20,2),
  _gold_run_id STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS workspace.gold.customer_performance (
  customer_id STRING,
  first_name STRING,
  last_name STRING,
  country STRING,
  total_orders BIGINT,
  total_quantity BIGINT,
  total_sales DECIMAL(20,2),
  average_order_value DECIMAL(20,2),
  _gold_run_id STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS workspace.gold.product_performance (
  product_id STRING,
  product_name STRING,
  category STRING,
  total_orders BIGINT,
  total_quantity BIGINT,
  total_sales DECIMAL(20,2),
  average_order_value DECIMAL(20,2),
  _gold_run_id STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS workspace.gold.kpi_daily (
  order_date DATE,
  total_orders BIGINT,
  total_quantity BIGINT,
  total_sales DECIMAL(20,2),
  average_order_value DECIMAL(20,2),
  _gold_run_id STRING
) USING DELTA;
