"""Completeness: primary keys must be present."""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col

from silver.rules import is_blank


def apply_customer_completeness(df: DataFrame) -> DataFrame:
    return df.withColumn("_r_CUST_PK_NULL", is_blank(col("customer_id")))


def apply_product_completeness(df: DataFrame) -> DataFrame:
    return df.withColumn("_r_PROD_PK_NULL", is_blank(col("product_id")))


def apply_order_completeness(df: DataFrame) -> DataFrame:
    return df.withColumn("_r_ORD_PK_NULL", is_blank(col("order_id")))
