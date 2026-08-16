"""Bronze ingest: land raw CSVs as string columns plus ingest metadata."""

from __future__ import annotations

from datetime import datetime, timezone

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import lit, to_timestamp

from pipeline.common.settings import (
    BRONZE_ENTITIES,
    BRONZE_SCHEMA,
    CATALOG_NAME,
    EXPECTED_BRONZE_COUNTS,
    RAW_DATA_PREFIX,
)
from pipeline.common.tables import ensure_schema, table_fqn, write_delta_overwrite


def raw_csv_path(raw_prefix: str, entity: str) -> str:
    return f"{raw_prefix.rstrip('/')}/{entity}.csv"


def read_raw_csv(spark: SparkSession, path: str) -> DataFrame:
    return (
        spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "false")
        .option("encoding", "UTF-8")
        .option("mode", "PERMISSIVE")
        .load(path)
    )


def add_ingest_metadata(
    df: DataFrame,
    ingest_file: str,
    ingest_ts: datetime,
    run_id: str,
) -> DataFrame:
    ingest_ts_str = ingest_ts.strftime("%Y-%m-%d %H:%M:%S")
    return (
        df.withColumn("_ingest_file", lit(ingest_file))
        .withColumn("_ingest_ts", to_timestamp(lit(ingest_ts_str)))
        .withColumn("_run_id", lit(run_id))
    )


def write_bronze_table(df: DataFrame, fqn: str) -> None:
    write_delta_overwrite(df, fqn)


def ingest_entity(
    spark: SparkSession,
    entity: str,
    raw_prefix: str,
    catalog: str | None,
    bronze_schema: str,
    ingest_ts: datetime,
    run_id: str,
) -> dict[str, object]:
    path = raw_csv_path(raw_prefix, entity)
    df = add_ingest_metadata(read_raw_csv(spark, path), path, ingest_ts, run_id)
    fqn = table_fqn(catalog, bronze_schema, entity)
    write_bronze_table(df, fqn)
    count = spark.table(fqn).count()
    return {
        "entity": entity,
        "source_path": path,
        "table": fqn,
        "row_count": count,
        "expected_row_count": EXPECTED_BRONZE_COUNTS.get(entity),
    }


def run_bronze_ingest(
    spark: SparkSession,
    raw_prefix: str = RAW_DATA_PREFIX,
    catalog: str | None = CATALOG_NAME,
    bronze_schema: str = BRONZE_SCHEMA,
    run_id: str | None = None,
) -> list[dict[str, object]]:
    catalog = catalog or None
    run_id = (run_id or "").strip() or datetime.now(timezone.utc).strftime(
        "bronze_%Y%m%dT%H%M%SZ"
    )
    ingest_ts = datetime.now(timezone.utc).replace(microsecond=0)

    ensure_schema(spark, catalog, bronze_schema)

    results = [
        ingest_entity(
            spark,
            entity,
            raw_prefix=raw_prefix,
            catalog=catalog,
            bronze_schema=bronze_schema,
            ingest_ts=ingest_ts,
            run_id=run_id,
        )
        for entity in BRONZE_ENTITIES
    ]
    return results
