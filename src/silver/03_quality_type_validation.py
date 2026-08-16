"""Type / format checks: email shape, allowed category, parseable order_date.

ORD_DATE_INVALID also fails dates after AS_OF_DATE. That future-date check is
the same named rule as in the generator; it is not split into a second flag.
"""

from datetime import date

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit, to_timestamp

from common.settings import AS_OF_DATE
from silver.rules import ALLOWED_CATEGORIES, EMAIL_PATTERN, is_blank


def apply_customer_type_validation(df: DataFrame) -> DataFrame:
    return df.withColumn(
        "_r_CUST_EMAIL_INVALID",
        is_blank(col("email")) | (~col("email").rlike(EMAIL_PATTERN)),
    )


def apply_product_type_validation(df: DataFrame) -> DataFrame:
    return df.withColumn(
        "_r_PROD_CATEGORY_INVALID",
        is_blank(col("category")) | (~col("category").isin(*ALLOWED_CATEGORIES)),
    )


def apply_order_type_validation(df: DataFrame, as_of_date: date = AS_OF_DATE) -> DataFrame:
    parsed = to_timestamp(col("order_date"), "yyyy-MM-dd HH:mm:ss")
    return df.withColumn(
        "_r_ORD_DATE_INVALID",
        parsed.isNull() | (parsed.cast("date") > lit(as_of_date)),
    )
