"""Business rules: non-negative prices, positive quantity, allowed order status."""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col

from silver.rules import ALLOWED_STATUSES, is_blank


def apply_product_business_logic(df: DataFrame) -> DataFrame:
    price = col("unit_price").cast("decimal(10,2)")
    return df.withColumn("_r_PROD_PRICE_NEGATIVE", price.isNull() | (price < 0))


def apply_order_business_logic(df: DataFrame) -> DataFrame:
    qty = col("quantity").cast("int")
    price = col("unit_price").cast("decimal(10,2)")
    return (
        df.withColumn("_r_ORD_QTY_INVALID", qty.isNull() | (qty <= 0))
        .withColumn("_r_ORD_PRICE_NEGATIVE", price.isNull() | (price < 0))
        .withColumn(
            "_r_ORD_STATUS_INVALID",
            is_blank(col("order_status")) | (~col("order_status").isin(*ALLOWED_STATUSES)),
        )
    )
