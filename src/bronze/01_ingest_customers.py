"""Bronze ingest for customers.csv → workspace.bronze.customers."""

from datetime import datetime, timezone

from pyspark.sql import SparkSession

from bronze.ingest_all import ingest_entity
from common.settings import BRONZE_SCHEMA, CATALOG_NAME, RAW_DATA_PREFIX


def ingest_customers(
    spark: SparkSession,
    raw_prefix: str = RAW_DATA_PREFIX,
    catalog: str | None = CATALOG_NAME,
    bronze_schema: str = BRONZE_SCHEMA,
    ingest_ts: datetime | None = None,
    run_id: str = "bronze_customers",
):
    ingest_ts = ingest_ts or datetime.now(timezone.utc).replace(microsecond=0)
    return ingest_entity(
        spark, "customers", raw_prefix, catalog, bronze_schema, ingest_ts, run_id
    )
