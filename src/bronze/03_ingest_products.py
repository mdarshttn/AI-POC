"""Bronze ingest for products.csv → workspace.bronze.products."""

from datetime import datetime, timezone

from pyspark.sql import SparkSession

from bronze.ingest_all import ingest_entity
from common.settings import BRONZE_SCHEMA, CATALOG_NAME, RAW_DATA_PREFIX


def ingest_products(
    spark: SparkSession,
    raw_prefix: str = RAW_DATA_PREFIX,
    catalog: str | None = CATALOG_NAME,
    bronze_schema: str = BRONZE_SCHEMA,
    ingest_ts: datetime | None = None,
    run_id: str = "bronze_products",
):
    ingest_ts = ingest_ts or datetime.now(timezone.utc).replace(microsecond=0)
    return ingest_entity(
        spark, "products", raw_prefix, catalog, bronze_schema, ingest_ts, run_id
    )
