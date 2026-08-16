"""Standalone e-commerce CSV generator. No Spark or Databricks imports."""

from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 42
AS_OF_DATE = date(2026, 8, 16)
SIGNUP_START = date(2020, 1, 1)

N_CUSTOMERS = 10_000
N_PRODUCTS = 500
N_ORDERS = 100_000
N_GOOD_CUSTOMERS = 9_996
N_GOOD_PRODUCTS = 495
N_GOOD_ORDERS = 99_991
EXPECTED_DEFECT_LOG_ROWS = 18

CUSTOMER_FIELDS = [
    "customer_id",
    "first_name",
    "last_name",
    "email",
    "signup_date",
    "country",
    "city",
]
PRODUCT_FIELDS = [
    "product_id",
    "product_name",
    "category",
    "unit_price",
    "in_stock",
]
ORDER_FIELDS = [
    "order_id",
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "unit_price",
    "order_status",
    "payment_method",
]
DEFECT_LOG_FIELDS = [
    "table",
    "rule_id",
    "record_id",
    "source_row",
    "column",
    "bad_value",
]

CATEGORIES = ["Electronics", "Home", "Fashion", "Sports", "Books"]
ORDER_STATUSES = ["pending", "paid", "shipped", "delivered", "cancelled"]
STATUS_WEIGHTS = [10, 25, 25, 30, 10]
PAYMENT_METHODS = ["card", "upi", "netbanking", "cod"]
COUNTRIES = [
    ("India", ["Mumbai", "Bengaluru", "Delhi", "Hyderabad", "Chennai"]),
    ("United States", ["New York", "Austin", "Seattle", "Chicago"]),
    ("United Kingdom", ["London", "Manchester", "Birmingham"]),
    ("Singapore", ["Singapore"]),
    ("United Arab Emirates", ["Dubai", "Abu Dhabi"]),
    ("Germany", ["Berlin", "Munich"]),
    ("Canada", ["Toronto", "Vancouver"]),
]
FIRST_NAMES = [
    "Aarav", "Aditi", "Amelia", "Arjun", "Aisha", "Ben", "Chen", "Diego",
    "Emma", "Fatima", "Grace", "Hassan", "Isha", "James", "Kavya", "Leo",
    "Maya", "Noah", "Olivia", "Priya", "Quinn", "Riya", "Samir", "Tara",
    "Uma", "Vikram", "Wei", "Yara", "Zane", "Sofia",
]
LAST_NAMES = [
    "Sharma", "Patel", "Khan", "Nguyen", "Garcia", "Smith", "Johnson",
    "Brown", "Lee", "Kim", "Singh", "Iyer", "Muller", "Costa", "Ali",
    "Chen", "Wilson", "Martin", "Ahmed", "Nair", "Lopez", "Wright",
    "Das", "Mehta", "Roy", "Park", "Silva", "Thomas", "Young", "Kapoor",
]
PRODUCT_ADJECTIVES = [
    "Aero", "Bold", "Classic", "Delta", "Eco", "Flex", "Prime", "Nova",
    "Urban", "Vista", "Lite", "Max", "Nimbus", "Pulse", "Ridge",
]
PRODUCT_NOUNS = [
    "Lamp", "Bottle", "Jacket", "Shoes", "Mug", "Bag", "Watch", "Speaker",
    "Chair", "Mat", "Hoodie", "Notebook", "Headphones", "Bottle", "Stand",
]

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "data"


def _slug(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum())


def _csv_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def _defect_entry(
    table: str,
    rule_id: str,
    record_id: str,
    column: str,
    bad_value: object,
) -> dict[str, str]:
    return {
        "table": table,
        "rule_id": rule_id,
        "record_id": record_id,
        "column": column,
        "bad_value": _csv_value(bad_value),
    }


def _random_date(rng: random.Random, start: date, end: date) -> date:
    span = (end - start).days
    return start + timedelta(days=rng.randint(0, span))


def _random_datetime(rng: random.Random, start: date, end: date) -> datetime:
    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end, datetime.max.time().replace(microsecond=0))
    span = int((end_dt - start_dt).total_seconds())
    return start_dt + timedelta(seconds=rng.randint(0, max(span, 0)))


def generate_good_customers(rng: random.Random) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for i in range(1, N_GOOD_CUSTOMERS + 1):
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        country, cities = rng.choice(COUNTRIES)
        rows.append(
            {
                "customer_id": f"CUST-{i:06d}",
                "first_name": first,
                "last_name": last,
                "email": f"{_slug(first)}.{_slug(last)}.{i}@example.com",
                "signup_date": _random_date(rng, SIGNUP_START, AS_OF_DATE),
                "country": country,
                "city": rng.choice(cities),
            }
        )
    return rows


def generate_good_products(rng: random.Random) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for i in range(1, N_GOOD_PRODUCTS + 1):
        category = CATEGORIES[(i - 1) % len(CATEGORIES)]
        name = (
            f"{rng.choice(PRODUCT_ADJECTIVES)} "
            f"{rng.choice(PRODUCT_NOUNS)} {i:04d}"
        )
        rows.append(
            {
                "product_id": f"PROD-{i:04d}",
                "product_name": f"{category} {name}",
                "category": category,
                "unit_price": round(rng.uniform(5.00, 999.99), 2),
                "in_stock": rng.randint(0, 500),
            }
        )
    return rows


def generate_good_orders(
    rng: random.Random,
    good_customers: list[dict[str, object]],
    good_products: list[dict[str, object]],
) -> list[dict[str, object]]:
    product_ids = [str(p["product_id"]) for p in good_products]
    products_by_id = {str(p["product_id"]): p for p in good_products}
    weights = [1.0 / (i + 1) for i in range(len(product_ids))]
    rows: list[dict[str, object]] = []
    for i in range(1, N_GOOD_ORDERS + 1):
        customer = rng.choice(good_customers)
        product_id = rng.choices(product_ids, weights=weights, k=1)[0]
        product = products_by_id[product_id]
        list_price = float(product["unit_price"])
        signup_date = customer["signup_date"]
        assert isinstance(signup_date, date)
        rows.append(
            {
                "order_id": f"ORD-{i:06d}",
                "customer_id": customer["customer_id"],
                "product_id": product_id,
                "order_date": _random_datetime(rng, signup_date, AS_OF_DATE),
                "quantity": rng.randint(1, 5),
                "unit_price": round(list_price * rng.uniform(0.80, 1.10), 2),
                "order_status": rng.choices(ORDER_STATUSES, weights=STATUS_WEIGHTS, k=1)[0],
                "payment_method": rng.choice(PAYMENT_METHODS),
            }
        )
    return rows


def inject_customer_defects() -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    rows: list[dict[str, object]] = [
        {
            "customer_id": "",
            "first_name": "Defect",
            "last_name": "NullPk",
            "email": "defect.nullpk@example.com",
            "signup_date": date(2024, 1, 15),
            "country": "India",
            "city": "Mumbai",
        },
        {
            "customer_id": "CUST-DUP-01",
            "first_name": "Defect",
            "last_name": "DupA",
            "email": "defect.dup.a@example.com",
            "signup_date": date(2024, 2, 1),
            "country": "India",
            "city": "Delhi",
        },
        {
            "customer_id": "CUST-DUP-01",
            "first_name": "Defect",
            "last_name": "DupB",
            "email": "defect.dup.b@example.com",
            "signup_date": date(2024, 2, 2),
            "country": "India",
            "city": "Bengaluru",
        },
        {
            "customer_id": "CUST-BAD-EML",
            "first_name": "Defect",
            "last_name": "BadEmail",
            "email": "not-an-email",
            "signup_date": date(2024, 3, 1),
            "country": "India",
            "city": "Chennai",
        },
    ]
    log = [
        _defect_entry("customers", "CUST_PK_NULL", "", "customer_id", ""),
        _defect_entry("customers", "CUST_PK_DUP", "CUST-DUP-01", "customer_id", "CUST-DUP-01"),
        _defect_entry("customers", "CUST_PK_DUP", "CUST-DUP-01", "customer_id", "CUST-DUP-01"),
        _defect_entry("customers", "CUST_EMAIL_INVALID", "CUST-BAD-EML", "email", "not-an-email"),
    ]
    return rows, log


def inject_product_defects() -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    rows: list[dict[str, object]] = [
        {
            "product_id": "",
            "product_name": "Defect Null PK",
            "category": "Home",
            "unit_price": 25.00,
            "in_stock": 10,
        },
        {
            "product_id": "PROD-DUP-01",
            "product_name": "Defect Duplicate A",
            "category": "Sports",
            "unit_price": 40.00,
            "in_stock": 12,
        },
        {
            "product_id": "PROD-DUP-01",
            "product_name": "Defect Duplicate B",
            "category": "Sports",
            "unit_price": 42.00,
            "in_stock": 8,
        },
        {
            "product_id": "PROD-BAD-CAT",
            "product_name": "Defect Invalid Category",
            "category": "Food",
            "unit_price": 15.00,
            "in_stock": 20,
        },
        {
            "product_id": "PROD-NEG-PRC",
            "product_name": "Defect Negative Price",
            "category": "Books",
            "unit_price": -10.00,
            "in_stock": 5,
        },
    ]
    log = [
        _defect_entry("products", "PROD_PK_NULL", "", "product_id", ""),
        _defect_entry("products", "PROD_PK_DUP", "PROD-DUP-01", "product_id", "PROD-DUP-01"),
        _defect_entry("products", "PROD_PK_DUP", "PROD-DUP-01", "product_id", "PROD-DUP-01"),
        _defect_entry("products", "PROD_CATEGORY_INVALID", "PROD-BAD-CAT", "category", "Food"),
        _defect_entry("products", "PROD_PRICE_NEGATIVE", "PROD-NEG-PRC", "unit_price", -10.00),
    ]
    return rows, log


def inject_order_defects() -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    good_customer_id = "CUST-000001"
    good_product_id = "PROD-0001"
    valid_when = datetime(2026, 6, 1, 10, 0, 0)

    def base_order(order_id: str) -> dict[str, object]:
        return {
            "order_id": order_id,
            "customer_id": good_customer_id,
            "product_id": good_product_id,
            "order_date": valid_when,
            "quantity": 1,
            "unit_price": 25.00,
            "order_status": "paid",
            "payment_method": "card",
        }

    dup_b = base_order("ORD-DUP-01")
    dup_b["payment_method"] = "upi"
    rows = [
        base_order(""),
        base_order("ORD-DUP-01"),
        dup_b,
        {**base_order("ORD-BAD-QTY"), "quantity": 0},
        {**base_order("ORD-BAD-PRC"), "unit_price": -5.00},
        {**base_order("ORD-BAD-STS"), "order_status": "SHIPPPED"},
        {**base_order("ORD-BAD-FCU"), "customer_id": "CUST-MISSING"},
        {**base_order("ORD-BAD-FPR"), "product_id": "PROD-MISSING"},
        {**base_order("ORD-BAD-DAT"), "order_date": datetime(2099, 12, 31, 23, 59, 59)},
    ]

    log = [
        _defect_entry("orders", "ORD_PK_NULL", "", "order_id", ""),
        _defect_entry("orders", "ORD_PK_DUP", "ORD-DUP-01", "order_id", "ORD-DUP-01"),
        _defect_entry("orders", "ORD_PK_DUP", "ORD-DUP-01", "order_id", "ORD-DUP-01"),
        _defect_entry("orders", "ORD_QTY_INVALID", "ORD-BAD-QTY", "quantity", 0),
        _defect_entry("orders", "ORD_PRICE_NEGATIVE", "ORD-BAD-PRC", "unit_price", -5.00),
        _defect_entry("orders", "ORD_STATUS_INVALID", "ORD-BAD-STS", "order_status", "SHIPPPED"),
        _defect_entry("orders", "ORD_FK_CUSTOMER", "ORD-BAD-FCU", "customer_id", "CUST-MISSING"),
        _defect_entry("orders", "ORD_FK_PRODUCT", "ORD-BAD-FPR", "product_id", "PROD-MISSING"),
        _defect_entry(
            "orders",
            "ORD_DATE_INVALID",
            "ORD-BAD-DAT",
            "order_date",
            datetime(2099, 12, 31, 23, 59, 59),
        ),
    ]
    return rows, log


def attach_source_rows(
    good_rows: list[dict[str, object]],
    defect_rows: list[dict[str, object]],
    defect_log: list[dict[str, str]],
) -> list[dict[str, str]]:
    if len(defect_rows) != len(defect_log):
        raise ValueError("Each defect row must have exactly one defect_log entry")
    offset = len(good_rows)
    numbered: list[dict[str, str]] = []
    for index, entry in enumerate(defect_log):
        numbered.append({**entry, "source_row": str(offset + index + 1)})
    return numbered


def write_csv(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, object]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _csv_value(row.get(field, "")) for field in fieldnames})


def validate(
    customers: list[dict[str, object]],
    products: list[dict[str, object]],
    orders: list[dict[str, object]],
    defect_log: list[dict[str, str]],
    good_customers: list[dict[str, object]],
    good_products: list[dict[str, object]],
    good_orders: list[dict[str, object]],
) -> None:
    errors: list[str] = []
    if len(customers) != N_CUSTOMERS:
        errors.append(f"customers: expected {N_CUSTOMERS}, got {len(customers)}")
    if len(products) != N_PRODUCTS:
        errors.append(f"products: expected {N_PRODUCTS}, got {len(products)}")
    if len(orders) != N_ORDERS:
        errors.append(f"orders: expected {N_ORDERS}, got {len(orders)}")
    if len(defect_log) != EXPECTED_DEFECT_LOG_ROWS:
        errors.append(
            f"defect_log: expected {EXPECTED_DEFECT_LOG_ROWS}, got {len(defect_log)}"
        )

    good_customer_ids = {str(row["customer_id"]) for row in good_customers}
    good_product_ids = {str(row["product_id"]) for row in good_products}
    for row in good_orders:
        if str(row["customer_id"]) not in good_customer_ids:
            errors.append(f"good order {row['order_id']} has invalid customer_id")
            break
        if str(row["product_id"]) not in good_product_ids:
            errors.append(f"good order {row['order_id']} has invalid product_id")
            break

    if errors:
        raise SystemExit("Validation failed:\n- " + "\n- ".join(errors))


def generate_all(
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, Path]:
    rng = random.Random(SEED)

    good_customers = generate_good_customers(rng)
    good_products = generate_good_products(rng)
    good_orders = generate_good_orders(rng, good_customers, good_products)

    customer_defects, customer_log = inject_customer_defects()
    product_defects, product_log = inject_product_defects()
    order_defects, order_log = inject_order_defects()

    customers = good_customers + customer_defects
    products = good_products + product_defects
    orders = good_orders + order_defects
    defect_log = (
        attach_source_rows(good_customers, customer_defects, customer_log)
        + attach_source_rows(good_products, product_defects, product_log)
        + attach_source_rows(good_orders, order_defects, order_log)
    )

    validate(
        customers,
        products,
        orders,
        defect_log,
        good_customers,
        good_products,
        good_orders,
    )

    paths = {
        "customers": output_dir / "customers.csv",
        "products": output_dir / "products.csv",
        "orders": output_dir / "orders.csv",
        "defect_log": output_dir / "defect_log.csv",
    }
    write_csv(paths["customers"], CUSTOMER_FIELDS, customers)
    write_csv(paths["products"], PRODUCT_FIELDS, products)
    write_csv(paths["orders"], ORDER_FIELDS, orders)
    write_csv(paths["defect_log"], DEFECT_LOG_FIELDS, defect_log)
    return paths


def _print_summary(paths: dict[str, Path]) -> None:
    print("Wrote:")
    for name, path in paths.items():
        with path.open(encoding="utf-8", newline="") as handle:
            row_count = sum(1 for _ in csv.DictReader(handle))
        print(f"  {path}  ({row_count} data rows)")

    print("\nDefect summary:")
    with paths["defect_log"].open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    counts: dict[str, int] = {}
    for row in rows:
        key = f"{row['table']}.{row['rule_id']}"
        counts[key] = counts.get(key, 0) + 1
    for key in sorted(counts):
        print(f"  {key}: {counts[key]}")
    print(f"  total defect_log rows: {len(rows)}")
    print("\nValidation passed.")


def main() -> None:
    paths = generate_all()
    _print_summary(paths)


if __name__ == "__main__":
    main()
