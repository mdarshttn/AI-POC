"""Shared pipeline locations. Change paths here, not in notebooks."""

RAW_DATA_PREFIX = "/Volumes/workspace/ai-poc/ai-data"
CATALOG_NAME = "workspace"
BRONZE_SCHEMA = "bronze"

BRONZE_ENTITIES = ("customers", "products", "orders")
DEFECT_LOG_FILENAME = "defect_log.csv"

EXPECTED_BRONZE_COUNTS = {
    "customers": 10_000,
    "products": 500,
    "orders": 100_000,
}
