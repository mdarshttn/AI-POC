"""Gold marts: business tables from clean Silver only."""

from __future__ import annotations

from datetime import datetime, timezone

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, count, lit, round as spark_round, sum as spark_sum, to_date, when

from pipeline.common.settings import CATALOG_NAME, GOLD_SCHEMA, SILVER_SCHEMA
from pipeline.common.tables import ensure_schema, table_fqn, write_delta_overwrite

CANCELLED_STATUS = "cancelled"


def _with_run_id(df: DataFrame, gold_run_id: str) -> DataFrame:
    return df.withColumn("_gold_run_id", lit(gold_run_id))


def _included_orders(fact_orders: DataFrame) -> DataFrame:
    return fact_orders.filter(col("order_status") != CANCELLED_STATUS)


def _with_aov(df: DataFrame) -> DataFrame:
    return df.withColumn(
        "average_order_value",
        when(
            col("total_orders") > 0,
            spark_round(col("total_sales") / col("total_orders"), 2),
        ),
    )


def build_dim_customer(silver_customers: DataFrame) -> DataFrame:
    return silver_customers.select(
        "customer_id",
        "first_name",
        "last_name",
        "email",
        "signup_date",
        "country",
        "city",
    )


def build_dim_product(silver_products: DataFrame) -> DataFrame:
    return silver_products.select(
        "product_id",
        "product_name",
        "category",
        col("unit_price").alias("list_unit_price"),
        "in_stock",
    )


def build_fact_orders(silver_orders: DataFrame) -> DataFrame:
    return silver_orders.select(
        "order_id",
        "customer_id",
        "product_id",
        to_date(col("order_date")).alias("order_date"),
        "quantity",
        "unit_price",
        (col("quantity") * col("unit_price")).alias("order_sales"),
        "order_status",
        "payment_method",
    )


def build_sales_performance(fact_orders: DataFrame) -> DataFrame:
    return _with_aov(
        _included_orders(fact_orders).agg(
            count("*").alias("total_orders"),
            spark_sum("quantity").alias("total_quantity"),
            spark_round(spark_sum("order_sales"), 2).alias("total_sales"),
        )
    )


def build_customer_performance(
    fact_orders: DataFrame,
    dim_customer: DataFrame,
) -> DataFrame:
    metrics = _with_aov(
        _included_orders(fact_orders)
        .groupBy("customer_id")
        .agg(
            count("*").alias("total_orders"),
            spark_sum("quantity").alias("total_quantity"),
            spark_round(spark_sum("order_sales"), 2).alias("total_sales"),
        )
    )
    return dim_customer.join(metrics, "customer_id", "inner").select(
        "customer_id",
        "first_name",
        "last_name",
        "country",
        "total_orders",
        "total_quantity",
        "total_sales",
        "average_order_value",
    )


def build_product_performance(
    fact_orders: DataFrame,
    dim_product: DataFrame,
) -> DataFrame:
    metrics = _with_aov(
        _included_orders(fact_orders)
        .groupBy("product_id")
        .agg(
            count("*").alias("total_orders"),
            spark_sum("quantity").alias("total_quantity"),
            spark_round(spark_sum("order_sales"), 2).alias("total_sales"),
        )
    )
    return dim_product.join(metrics, "product_id", "inner").select(
        "product_id",
        "product_name",
        "category",
        "total_orders",
        "total_quantity",
        "total_sales",
        "average_order_value",
    )


def build_kpi_daily(fact_orders: DataFrame) -> DataFrame:
    return _with_aov(
        _included_orders(fact_orders)
        .groupBy("order_date")
        .agg(
            count("*").alias("total_orders"),
            spark_sum("quantity").alias("total_quantity"),
            spark_round(spark_sum("order_sales"), 2).alias("total_sales"),
        )
    )


def run_gold_build(
    spark: SparkSession,
    catalog: str | None = CATALOG_NAME,
    silver_schema: str = SILVER_SCHEMA,
    gold_schema: str = GOLD_SCHEMA,
    run_id: str | None = None,
) -> list[dict[str, object]]:
    catalog = catalog or None
    gold_run_id = (run_id or "").strip() or datetime.now(timezone.utc).strftime(
        "gold_%Y%m%dT%H%M%SZ"
    )

    ensure_schema(spark, catalog, gold_schema)

    silver_customers = spark.table(table_fqn(catalog, silver_schema, "customers"))
    silver_products = spark.table(table_fqn(catalog, silver_schema, "products"))
    silver_orders = spark.table(table_fqn(catalog, silver_schema, "orders"))

    dim_customer = build_dim_customer(silver_customers)
    dim_product = build_dim_product(silver_products)
    fact_orders = build_fact_orders(silver_orders)
    sales_performance = build_sales_performance(fact_orders)
    customer_performance = build_customer_performance(fact_orders, dim_customer)
    product_performance = build_product_performance(fact_orders, dim_product)
    kpi_daily = build_kpi_daily(fact_orders)

    outputs = (
        ("dim_customer", dim_customer),
        ("dim_product", dim_product),
        ("fact_orders", fact_orders),
        ("sales_performance", sales_performance),
        ("customer_performance", customer_performance),
        ("product_performance", product_performance),
        ("kpi_daily", kpi_daily),
    )

    summary = []
    for table_name, df in outputs:
        out = _with_run_id(df, gold_run_id)
        fqn = table_fqn(catalog, gold_schema, table_name)
        write_delta_overwrite(out, fqn)
        summary.append({"table": fqn, "row_count": spark.table(fqn).count()})

    silver_order_count = silver_orders.count()
    fact_count = spark.table(table_fqn(catalog, gold_schema, "fact_orders")).count()
    if fact_count != silver_order_count:
        raise ValueError(
            f"gold.fact_orders count {fact_count} != silver.orders count {silver_order_count}"
        )
    sales_rows = spark.table(table_fqn(catalog, gold_schema, "sales_performance")).count()
    if sales_rows != 1:
        raise ValueError(f"gold.sales_performance should have 1 row, got {sales_rows}")

    return summary
