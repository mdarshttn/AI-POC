"""Uniqueness: both duplicate primary-key rows fail. Blank PKs are not treated as dups."""

from pyspark.sql import DataFrame

from silver.rules import with_dup_flag


def apply_customer_uniqueness(df: DataFrame) -> DataFrame:
    return with_dup_flag(df, "customer_id", "_r_CUST_PK_DUP")


def apply_product_uniqueness(df: DataFrame) -> DataFrame:
    return with_dup_flag(df, "product_id", "_r_PROD_PK_DUP")


def apply_order_uniqueness(df: DataFrame) -> DataFrame:
    return with_dup_flag(df, "order_id", "_r_ORD_PK_DUP")
