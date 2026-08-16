from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from data_generation.generate_sample_data import (  # noqa: E402
    EXPECTED_DEFECT_LOG_ROWS,
    N_CUSTOMERS,
    N_ORDERS,
    N_PRODUCTS,
    generate_good_customers,
    generate_good_orders,
    generate_good_products,
    inject_customer_defects,
    inject_order_defects,
    inject_product_defects,
    validate,
)
import random


class TestDataGeneration(unittest.TestCase):
    def test_customer_defect_block(self):
        rows, log = inject_customer_defects()
        self.assertEqual(len(rows), 4)
        self.assertEqual(len(log), 4)
        self.assertEqual(
            [entry["rule_id"] for entry in log],
            ["CUST_PK_NULL", "CUST_PK_DUP", "CUST_PK_DUP", "CUST_EMAIL_INVALID"],
        )
        self.assertEqual(rows[0]["customer_id"], "")
        self.assertEqual(rows[1]["customer_id"], rows[2]["customer_id"])
        self.assertEqual(rows[3]["email"], "not-an-email")

    def test_product_defect_block(self):
        rows, log = inject_product_defects()
        self.assertEqual(len(rows), 5)
        self.assertEqual(
            [entry["rule_id"] for entry in log],
            [
                "PROD_PK_NULL",
                "PROD_PK_DUP",
                "PROD_PK_DUP",
                "PROD_CATEGORY_INVALID",
                "PROD_PRICE_NEGATIVE",
            ],
        )
        self.assertEqual(rows[3]["category"], "Food")
        self.assertEqual(rows[4]["unit_price"], -10.00)

    def test_order_defect_block(self):
        rows, log = inject_order_defects()
        self.assertEqual(len(rows), 9)
        self.assertEqual(len(log), 9)
        rule_ids = [entry["rule_id"] for entry in log]
        self.assertIn("ORD_FK_CUSTOMER", rule_ids)
        self.assertIn("ORD_FK_PRODUCT", rule_ids)
        self.assertIn("ORD_DATE_INVALID", rule_ids)
        self.assertEqual(rows[3]["quantity"], 0)
        self.assertEqual(rows[5]["order_status"], "SHIPPPED")

    def test_good_orders_only_reference_good_ids(self):
        rng = random.Random(42)
        customers = generate_good_customers(rng)
        products = generate_good_products(rng)
        orders = generate_good_orders(rng, customers, products)
        customer_ids = {row["customer_id"] for row in customers}
        product_ids = {row["product_id"] for row in products}
        for row in orders:
            self.assertIn(row["customer_id"], customer_ids)
            self.assertIn(row["product_id"], product_ids)

    def test_validate_rejects_wrong_counts(self):
        with self.assertRaises(SystemExit):
            validate([], [], [], [], [], [], [])

    def test_committed_csv_counts_if_present(self):
        data_dir = ROOT / "data"
        customers = data_dir / "customers.csv"
        if not customers.exists():
            self.skipTest("data/customers.csv not generated yet")
        counts = {}
        for name in ("customers", "products", "orders", "defect_log"):
            path = data_dir / f"{name}.csv"
            with path.open(encoding="utf-8", newline="") as handle:
                counts[name] = sum(1 for _ in csv.DictReader(handle))
        self.assertEqual(counts["customers"], N_CUSTOMERS)
        self.assertEqual(counts["products"], N_PRODUCTS)
        self.assertEqual(counts["orders"], N_ORDERS)
        self.assertEqual(counts["defect_log"], EXPECTED_DEFECT_LOG_ROWS)


if __name__ == "__main__":
    unittest.main()
