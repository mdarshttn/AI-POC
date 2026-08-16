"""Delta table helpers shared by Bronze and Silver."""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession


def table_fqn(catalog: str | None, schema: str, table: str) -> str:
    if catalog:
        return f"`{catalog}`.`{schema}`.`{table}`"
    return f"`{schema}`.`{table}`"


def ensure_schema(spark: SparkSession, catalog: str | None, schema: str) -> None:
    if catalog:
        spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.`{schema}`")
        return
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{schema}`")


def write_delta_overwrite(df: DataFrame, fqn: str) -> None:
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(fqn)
    )
