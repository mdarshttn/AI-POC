"""Silver cleanse: type Bronze strings, quarantine named DQ failures."""

from __future__ import annotations

import importlib.util
from datetime import date, datetime, timezone
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import coalesce, col, concat_ws, lit, to_date, to_timestamp, when

from common.settings import (
    AS_OF_DATE,
    BRONZE_SCHEMA,
    CATALOG_NAME,
    EXPECTED_DQ_RESULTS_ROWS,
    EXPECTED_QUARANTINE_COUNTS,
    EXPECTED_SILVER_COUNTS,
    OPS_SCHEMA,
    SILVER_SCHEMA,
)
from common.tables import ensure_schema, table_fqn, write_delta_overwrite
from silver.rules import (
    CUSTOMER_PAYLOAD,
    CUSTOMER_RULES,
    ORDER_PAYLOAD,
    ORDER_RULES,
    PRODUCT_PAYLOAD,
    PRODUCT_RULES,
    RULE_MESSAGES,
    any_flag,
    with_fingerprint,
)


def _load_quality_module(filename: str):
    path = Path(__file__).resolve().parent / filename
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load quality module {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_completeness = _load_quality_module("01_quality_completeness.py")
_uniqueness = _load_quality_module("02_quality_uniqueness.py")
_type_validation = _load_quality_module("03_quality_type_validation.py")
_referential = _load_quality_module("04_quality_referential_integrity.py")
_business = _load_quality_module("05_quality_business_logic.py")


def _type_customers(df: DataFrame, silver_run_id: str) -> DataFrame:
    return df.select(
        col("customer_id"),
        col("first_name"),
        col("last_name"),
        col("email"),
        to_date(col("signup_date"), "yyyy-MM-dd").alias("signup_date"),
        col("country"),
        col("city"),
        col("_ingest_file"),
        col("_ingest_ts"),
        col("_run_id").alias("_bronze_run_id"),
        lit(silver_run_id).alias("_silver_run_id"),
    )


def _type_products(df: DataFrame, silver_run_id: str) -> DataFrame:
    return df.select(
        col("product_id"),
        col("product_name"),
        col("category"),
        col("unit_price").cast("decimal(10,2)").alias("unit_price"),
        col("in_stock").cast("int").alias("in_stock"),
        col("_ingest_file"),
        col("_ingest_ts"),
        col("_run_id").alias("_bronze_run_id"),
        lit(silver_run_id).alias("_silver_run_id"),
    )


def _type_orders(df: DataFrame, silver_run_id: str) -> DataFrame:
    return df.select(
        col("order_id"),
        col("customer_id"),
        col("product_id"),
        to_timestamp(col("order_date"), "yyyy-MM-dd HH:mm:ss").alias("order_date"),
        col("quantity").cast("int").alias("quantity"),
        col("unit_price").cast("decimal(10,2)").alias("unit_price"),
        col("order_status"),
        col("payment_method"),
        col("_ingest_file"),
        col("_ingest_ts"),
        col("_run_id").alias("_bronze_run_id"),
        lit(silver_run_id).alias("_silver_run_id"),
    )


def _select_quarantine(
    df: DataFrame,
    payload_cols: list[str],
    rules: tuple,
    silver_run_id: str,
) -> DataFrame:
    failed = df.filter(any_flag(rules))
    rule_id_expr = concat_ws(
        ",", *[when(col(flag), lit(rule_id)) for rule_id, flag, _ in rules]
    )
    failed_column = coalesce(
        *[when(col(flag), lit(failed_col)) for _, flag, failed_col in rules]
    )
    failed_value = coalesce(
        *[when(col(flag), col(failed_col).cast("string")) for _, flag, failed_col in rules]
    )
    return failed.select(
        *[col(c) for c in payload_cols],
        col("_ingest_file"),
        col("_ingest_ts"),
        col("_run_id").alias("_bronze_run_id"),
        lit(silver_run_id).alias("_silver_run_id"),
        col("_row_fingerprint"),
        rule_id_expr.alias("_rule_id"),
        failed_column.alias("_failed_column"),
        failed_value.alias("_failed_value"),
    )


def _select_dq_results(
    df: DataFrame,
    table_name: str,
    pk_col: str,
    rules: tuple,
    silver_run_id: str,
) -> DataFrame:
    frames = []
    for rule_id, flag, failed_col in rules:
        frames.append(
            df.filter(col(flag)).select(
                lit(silver_run_id).alias("silver_run_id"),
                col("_run_id").alias("bronze_run_id"),
                lit(table_name).alias("table_name"),
                lit(rule_id).alias("rule_id"),
                coalesce(col(pk_col).cast("string"), lit("")).alias("record_id"),
                col("_row_fingerprint").alias("row_fingerprint"),
                lit(failed_col).alias("failed_column"),
                coalesce(col(failed_col).cast("string"), lit("")).alias("failed_value"),
                lit("error").alias("severity"),
                lit(RULE_MESSAGES[rule_id]).alias("message"),
            )
        )
    result = frames[0]
    for frame in frames[1:]:
        result = result.unionByName(frame)
    return result


def _split(
    flagged: DataFrame,
    payload_cols: list[str],
    pk_col: str,
    rules: tuple,
    table_name: str,
    silver_run_id: str,
    type_fn,
) -> tuple[DataFrame, DataFrame, DataFrame]:
    valid = type_fn(flagged.filter(~any_flag(rules)), silver_run_id)
    quarantine = _select_quarantine(flagged, payload_cols, rules, silver_run_id)
    dq_results = _select_dq_results(flagged, table_name, pk_col, rules, silver_run_id)
    return valid, quarantine, dq_results


def _flag_customers(bronze_customers: DataFrame) -> DataFrame:
    df = with_fingerprint(bronze_customers, CUSTOMER_PAYLOAD)
    df = _completeness.apply_customer_completeness(df)
    df = _uniqueness.apply_customer_uniqueness(df)
    df = _type_validation.apply_customer_type_validation(df)
    return df


def _flag_products(bronze_products: DataFrame) -> DataFrame:
    df = with_fingerprint(bronze_products, PRODUCT_PAYLOAD)
    df = _completeness.apply_product_completeness(df)
    df = _uniqueness.apply_product_uniqueness(df)
    df = _type_validation.apply_product_type_validation(df)
    df = _business.apply_product_business_logic(df)
    return df


def _flag_orders(
    bronze_orders: DataFrame,
    silver_customers: DataFrame,
    silver_products: DataFrame,
    as_of_date: date,
) -> DataFrame:
    df = with_fingerprint(bronze_orders, ORDER_PAYLOAD)
    df = _completeness.apply_order_completeness(df)
    df = _uniqueness.apply_order_uniqueness(df)
    df = _type_validation.apply_order_type_validation(df, as_of_date=as_of_date)
    df = _business.apply_order_business_logic(df)
    df = _referential.apply_order_referential_integrity(
        df, silver_customers, silver_products
    )
    return df


def run_silver_transform(
    spark: SparkSession,
    catalog: str | None = CATALOG_NAME,
    bronze_schema: str = BRONZE_SCHEMA,
    silver_schema: str = SILVER_SCHEMA,
    ops_schema: str = OPS_SCHEMA,
    run_id: str | None = None,
    as_of_date: date = AS_OF_DATE,
) -> list[dict[str, object]]:
    catalog = catalog or None
    silver_run_id = (run_id or "").strip() or datetime.now(timezone.utc).strftime(
        "silver_%Y%m%dT%H%M%SZ"
    )

    ensure_schema(spark, catalog, silver_schema)
    ensure_schema(spark, catalog, ops_schema)

    bronze_customers = spark.table(table_fqn(catalog, bronze_schema, "customers"))
    bronze_products = spark.table(table_fqn(catalog, bronze_schema, "products"))
    bronze_orders = spark.table(table_fqn(catalog, bronze_schema, "orders"))

    silver_customers, q_customers, dq_customers = _split(
        _flag_customers(bronze_customers),
        CUSTOMER_PAYLOAD,
        "customer_id",
        CUSTOMER_RULES,
        "customers",
        silver_run_id,
        _type_customers,
    )
    silver_products, q_products, dq_products = _split(
        _flag_products(bronze_products),
        PRODUCT_PAYLOAD,
        "product_id",
        PRODUCT_RULES,
        "products",
        silver_run_id,
        _type_products,
    )

    write_delta_overwrite(silver_customers, table_fqn(catalog, silver_schema, "customers"))
    write_delta_overwrite(q_customers, table_fqn(catalog, ops_schema, "quarantine_customers"))
    write_delta_overwrite(silver_products, table_fqn(catalog, silver_schema, "products"))
    write_delta_overwrite(q_products, table_fqn(catalog, ops_schema, "quarantine_products"))

    clean_customers = spark.table(table_fqn(catalog, silver_schema, "customers"))
    clean_products = spark.table(table_fqn(catalog, silver_schema, "products"))

    silver_orders, q_orders, dq_orders = _split(
        _flag_orders(bronze_orders, clean_customers, clean_products, as_of_date),
        ORDER_PAYLOAD,
        "order_id",
        ORDER_RULES,
        "orders",
        silver_run_id,
        _type_orders,
    )
    write_delta_overwrite(silver_orders, table_fqn(catalog, silver_schema, "orders"))
    write_delta_overwrite(q_orders, table_fqn(catalog, ops_schema, "quarantine_orders"))

    dq_results = dq_customers.unionByName(dq_products).unionByName(dq_orders)
    write_delta_overwrite(dq_results, table_fqn(catalog, ops_schema, "dq_results"))

    summary = []
    for entity, bronze_df, silver_name, quarantine_name in (
        ("customers", bronze_customers, "customers", "quarantine_customers"),
        ("products", bronze_products, "products", "quarantine_products"),
        ("orders", bronze_orders, "orders", "quarantine_orders"),
    ):
        bronze_count = bronze_df.count()
        silver_count = spark.table(table_fqn(catalog, silver_schema, silver_name)).count()
        quarantine_count = spark.table(
            table_fqn(catalog, ops_schema, quarantine_name)
        ).count()
        summary.append(
            {
                "entity": entity,
                "bronze_count": bronze_count,
                "silver_count": silver_count,
                "quarantine_count": quarantine_count,
                "expected_silver": EXPECTED_SILVER_COUNTS[entity],
                "expected_quarantine": EXPECTED_QUARANTINE_COUNTS[entity],
                "conserved": bronze_count == silver_count + quarantine_count,
            }
        )

    dq_count = spark.table(table_fqn(catalog, ops_schema, "dq_results")).count()
    errors = []
    for row in summary:
        if not row["conserved"]:
            errors.append(
                f"{row['entity']}: bronze {row['bronze_count']} != "
                f"silver {row['silver_count']} + quarantine {row['quarantine_count']}"
            )
        if row["silver_count"] != row["expected_silver"]:
            errors.append(
                f"{row['entity']} silver: expected {row['expected_silver']}, "
                f"got {row['silver_count']}"
            )
        if row["quarantine_count"] != row["expected_quarantine"]:
            errors.append(
                f"{row['entity']} quarantine: expected {row['expected_quarantine']}, "
                f"got {row['quarantine_count']}"
            )
    if dq_count != EXPECTED_DQ_RESULTS_ROWS:
        errors.append(f"dq_results: expected {EXPECTED_DQ_RESULTS_ROWS}, got {dq_count}")
    if errors:
        raise ValueError("Silver validation failed:\n- " + "\n- ".join(errors))

    return summary
