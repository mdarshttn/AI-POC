"""Named Silver DQ rules. Booleans only — no extra rule ids."""

from __future__ import annotations

from datetime import date

from pyspark.sql import DataFrame
from pyspark.sql.functions import coalesce, col, concat_ws, count, lit, sha2, to_timestamp, trim, when
from pyspark.sql.window import Window

from pipeline.common.settings import AS_OF_DATE

ALLOWED_CATEGORIES = ("Electronics", "Home", "Fashion", "Sports", "Books")
ALLOWED_STATUSES = ("pending", "paid", "shipped", "delivered", "cancelled")
EMAIL_PATTERN = r".+@.+\..+"

CUSTOMER_PAYLOAD = [
    "customer_id",
    "first_name",
    "last_name",
    "email",
    "signup_date",
    "country",
    "city",
]
PRODUCT_PAYLOAD = [
    "product_id",
    "product_name",
    "category",
    "unit_price",
    "in_stock",
]
ORDER_PAYLOAD = [
    "order_id",
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "unit_price",
    "order_status",
    "payment_method",
]

# (rule_id, flag_column, failed_column)
CUSTOMER_RULES = (
    ("CUST_PK_NULL", "_r_CUST_PK_NULL", "customer_id"),
    ("CUST_PK_DUP", "_r_CUST_PK_DUP", "customer_id"),
    ("CUST_EMAIL_INVALID", "_r_CUST_EMAIL_INVALID", "email"),
)
PRODUCT_RULES = (
    ("PROD_PK_NULL", "_r_PROD_PK_NULL", "product_id"),
    ("PROD_PK_DUP", "_r_PROD_PK_DUP", "product_id"),
    ("PROD_CATEGORY_INVALID", "_r_PROD_CATEGORY_INVALID", "category"),
    ("PROD_PRICE_NEGATIVE", "_r_PROD_PRICE_NEGATIVE", "unit_price"),
)
ORDER_RULES = (
    ("ORD_PK_NULL", "_r_ORD_PK_NULL", "order_id"),
    ("ORD_PK_DUP", "_r_ORD_PK_DUP", "order_id"),
    ("ORD_QTY_INVALID", "_r_ORD_QTY_INVALID", "quantity"),
    ("ORD_PRICE_NEGATIVE", "_r_ORD_PRICE_NEGATIVE", "unit_price"),
    ("ORD_STATUS_INVALID", "_r_ORD_STATUS_INVALID", "order_status"),
    ("ORD_DATE_INVALID", "_r_ORD_DATE_INVALID", "order_date"),
    ("ORD_FK_CUSTOMER", "_r_ORD_FK_CUSTOMER", "customer_id"),
    ("ORD_FK_PRODUCT", "_r_ORD_FK_PRODUCT", "product_id"),
)

RULE_MESSAGES = {
    "CUST_PK_NULL": "customer_id is missing",
    "CUST_PK_DUP": "customer_id is not unique",
    "CUST_EMAIL_INVALID": "email is not a valid address",
    "PROD_PK_NULL": "product_id is missing",
    "PROD_PK_DUP": "product_id is not unique",
    "PROD_CATEGORY_INVALID": "category is not in the allowed list",
    "PROD_PRICE_NEGATIVE": "unit_price is missing or < 0",
    "ORD_PK_NULL": "order_id is missing",
    "ORD_PK_DUP": "order_id is not unique",
    "ORD_QTY_INVALID": "quantity is missing or <= 0",
    "ORD_PRICE_NEGATIVE": "unit_price is missing or < 0",
    "ORD_STATUS_INVALID": "order_status is not in the allowed list",
    "ORD_DATE_INVALID": "order_date is unparseable or after AS_OF_DATE",
    "ORD_FK_CUSTOMER": "customer_id is not in silver.customers",
    "ORD_FK_PRODUCT": "product_id is not in silver.products",
}


def is_blank(column):
    return column.isNull() | (trim(column.cast("string")) == lit(""))


def any_flag(rules: tuple) -> object:
    expr = col(rules[0][1])
    for _, flag, _ in rules[1:]:
        expr = expr | col(flag)
    return expr


def with_fingerprint(df: DataFrame, payload_cols: list[str]) -> DataFrame:
    parts = [coalesce(col(c).cast("string"), lit("")) for c in payload_cols]
    return df.withColumn("_row_fingerprint", sha2(concat_ws("||", *parts), 256))


def with_dup_flag(df: DataFrame, pk_col: str, flag_name: str) -> DataFrame:
    pk = col(pk_col)
    window = Window.partitionBy(pk_col)
    return df.withColumn(
        flag_name,
        when(is_blank(pk), lit(False)).otherwise(count(lit(1)).over(window) > 1),
    )


def add_customer_flags(df: DataFrame) -> DataFrame:
    df = with_fingerprint(df, CUSTOMER_PAYLOAD)
    df = with_dup_flag(df, "customer_id", "_r_CUST_PK_DUP")
    return (
        df.withColumn("_r_CUST_PK_NULL", is_blank(col("customer_id")))
        .withColumn(
            "_r_CUST_EMAIL_INVALID",
            is_blank(col("email")) | (~col("email").rlike(EMAIL_PATTERN)),
        )
    )


def add_product_flags(df: DataFrame) -> DataFrame:
    price = col("unit_price").cast("decimal(10,2)")
    df = with_fingerprint(df, PRODUCT_PAYLOAD)
    df = with_dup_flag(df, "product_id", "_r_PROD_PK_DUP")
    return (
        df.withColumn("_r_PROD_PK_NULL", is_blank(col("product_id")))
        .withColumn(
            "_r_PROD_CATEGORY_INVALID",
            is_blank(col("category")) | (~col("category").isin(*ALLOWED_CATEGORIES)),
        )
        .withColumn("_r_PROD_PRICE_NEGATIVE", price.isNull() | (price < 0))
    )


def add_order_base_flags(df: DataFrame, as_of_date: date = AS_OF_DATE) -> DataFrame:
    qty = col("quantity").cast("int")
    price = col("unit_price").cast("decimal(10,2)")
    parsed = to_timestamp(col("order_date"), "yyyy-MM-dd HH:mm:ss")
    df = with_fingerprint(df, ORDER_PAYLOAD)
    df = with_dup_flag(df, "order_id", "_r_ORD_PK_DUP")
    return (
        df.withColumn("_r_ORD_PK_NULL", is_blank(col("order_id")))
        .withColumn("_r_ORD_QTY_INVALID", qty.isNull() | (qty <= 0))
        .withColumn("_r_ORD_PRICE_NEGATIVE", price.isNull() | (price < 0))
        .withColumn(
            "_r_ORD_STATUS_INVALID",
            is_blank(col("order_status")) | (~col("order_status").isin(*ALLOWED_STATUSES)),
        )
        .withColumn(
            "_r_ORD_DATE_INVALID",
            parsed.isNull() | (parsed.cast("date") > lit(as_of_date)),
        )
    )


def add_order_fk_flags(
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
