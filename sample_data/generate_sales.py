
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

products = [
    ("Laptop", "Electronics", 950),
    ("Monitor", "Electronics", 240),
    ("Keyboard", "Accessories", 75),
    ("Mouse", "Accessories", 35),
    ("Desk", "Furniture", 320),
    ("Office Chair", "Furniture", 180),
    ("Headphones", "Electronics", 120),
    ("Webcam", "Electronics", 85),
]

regions = ["North", "South", "East", "West"]

output = Path(__file__).with_name("sales.csv")

with output.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "order_id",
        "order_date",
        "product",
        "category",
        "region",
        "quantity",
        "unit_price",
        "revenue",
    ])

    for order_id in range(1, 501):
        product, category, base_price = random.choice(products)
        quantity = random.randint(1, 8)
        region = random.choice(regions)

        order_date = (
            date(2025, 1, 1)
            + timedelta(days=random.randint(0, 364))
        )

        writer.writerow([
            order_id,
            order_date.isoformat(),
            product,
            category,
            region,
            quantity,
            base_price,
            quantity * base_price,
        ])

print(f"Created {output} with 500 sales records")
