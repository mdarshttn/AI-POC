"""Referential integrity: order FKs must exist in clean Silver dimensions."""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit


def apply_order_referential_integrity(
    df: DataFrame,
    silver_customers: DataFrame,
    silver_products: DataFrame,
) -> DataFrame:
    cust_ok = silver_customers.select("customer_id").distinct().withColumn("_cust_ok", lit(True))
    prod_ok = silver_products.select("product_id").distinct().withColumn("_prod_ok", lit(True))
    df = df.join(cust_ok, on="customer_id", how="left")
    df = df.join(prod_ok, on="product_id", how="left")
    return df.withColumn("_r_ORD_FK_CUSTOMER", col("_cust_ok").isNull()).withColumn(
        "_r_ORD_FK_PRODUCT", col("_prod_ok").isNull()
    )
