"""Shared pipeline locations. Change paths here, not in notebooks."""

from datetime import date

RAW_DATA_PREFIX = "/Volumes/workspace/ai-poc/ai-data"
CATALOG_NAME = "workspace"
BRONZE_SCHEMA = "bronze"
SILVER_SCHEMA = "silver"
OPS_SCHEMA = "ops"
AS_OF_DATE = date(2026, 8, 16)

BRONZE_ENTITIES = ("customers", "products", "orders")
DEFECT_LOG_FILENAME = "defect_log.csv"

EXPECTED_BRONZE_COUNTS = {
    "customers": 10_000,
    "products": 500,
    "orders": 100_000,
}
EXPECTED_SILVER_COUNTS = {
    "customers": 9_996,
    "products": 495,
    "orders": 99_991,
}
EXPECTED_QUARANTINE_COUNTS = {
    "customers": 4,
    "products": 5,
    "orders": 9,
}
EXPECTED_DQ_RESULTS_ROWS = 18
