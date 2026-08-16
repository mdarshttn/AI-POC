from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from common.settings import (  # noqa: E402
    EXPECTED_BRONZE_COUNTS,
    EXPECTED_DQ_RESULTS_ROWS,
    EXPECTED_QUARANTINE_COUNTS,
    EXPECTED_SILVER_COUNTS,
)


class TestQualityContracts(unittest.TestCase):
    def test_conservation_per_entity(self):
        for entity in ("customers", "products", "orders"):
            self.assertEqual(
                EXPECTED_BRONZE_COUNTS[entity],
                EXPECTED_SILVER_COUNTS[entity] + EXPECTED_QUARANTINE_COUNTS[entity],
                msg=entity,
            )

    def test_seeded_dq_results_total(self):
        self.assertEqual(EXPECTED_DQ_RESULTS_ROWS, 18)
        self.assertEqual(sum(EXPECTED_QUARANTINE_COUNTS.values()), 18)

    def test_quality_modules_exist(self):
        silver = ROOT / "src" / "silver"
        expected = (
            "01_quality_completeness.py",
            "02_quality_uniqueness.py",
            "03_quality_type_validation.py",
            "04_quality_referential_integrity.py",
            "05_quality_business_logic.py",
            "create_silver_tables.py",
        )
        for name in expected:
            self.assertTrue((silver / name).is_file(), name)

    def test_quality_modules_contain_named_rules(self):
        completeness = (ROOT / "src" / "silver" / "01_quality_completeness.py").read_text(
            encoding="utf-8"
        )
        uniqueness = (ROOT / "src" / "silver" / "02_quality_uniqueness.py").read_text(
            encoding="utf-8"
        )
        referential = (
            ROOT / "src" / "silver" / "04_quality_referential_integrity.py"
        ).read_text(encoding="utf-8")
        self.assertIn("_r_CUST_PK_NULL", completeness)
        self.assertIn("_r_CUST_PK_DUP", uniqueness)
        self.assertIn("_r_ORD_FK_CUSTOMER", referential)
        self.assertIn("_r_ORD_FK_PRODUCT", referential)


if __name__ == "__main__":
    unittest.main()
