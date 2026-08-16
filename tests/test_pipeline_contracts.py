from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestPipelineContracts(unittest.TestCase):
    def test_bronze_silver_gold_entrypoints(self):
        self.assertTrue((ROOT / "src" / "bronze" / "ingest_all.py").is_file())
        self.assertTrue((ROOT / "src" / "silver" / "create_silver_tables.py").is_file())
        self.assertTrue((ROOT / "src" / "gold" / "create_gold_tables.py").is_file())
        self.assertTrue((ROOT / "database" / "schema.sql").is_file())
        self.assertTrue((ROOT / "database" / "seed-data-notes.md").is_file())
        self.assertTrue((ROOT / "database" / "setup-notes.md").is_file())

    def test_three_gold_aggregations_present(self):
        sales = (ROOT / "src" / "gold" / "01_sales_by_product.sql").read_text(
            encoding="utf-8"
        )
        revenue = (ROOT / "src" / "gold" / "02_revenue_by_customer.sql").read_text(
            encoding="utf-8"
        )
        trends = (ROOT / "src" / "gold" / "03_daily_weekly_trends.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn("workspace.gold.product_performance", sales)
        self.assertIn("workspace.gold.customer_performance", revenue)
        self.assertIn("workspace.gold.kpi_daily", trends)
        self.assertIn("date_trunc('WEEK'", trends)

    def test_gold_python_writes_performance_tables(self):
        source = (ROOT / "src" / "gold" / "create_gold_tables.py").read_text(
            encoding="utf-8"
        )
        for name in (
            "build_sales_performance",
            "build_customer_performance",
            "build_product_performance",
            "build_kpi_daily",
        ):
            self.assertIn(name, source)

    def test_schema_sql_creates_medallion_schemas(self):
        schema = (ROOT / "database" / "schema.sql").read_text(encoding="utf-8")
        for name in ("bronze", "silver", "ops", "gold"):
            self.assertIn(f"workspace.{name}", schema)

    def test_notebooks_exist(self):
        for name in (
            "01_bronze_ingest.py",
            "02_silver_transform.py",
            "03_gold_build.py",
        ):
            self.assertTrue((ROOT / "notebooks" / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
