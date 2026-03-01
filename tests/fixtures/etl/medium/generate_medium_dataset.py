import csv
from datetime import datetime, timedelta
from random import Random

COUNTRIES = [
    ("US", "United States"),
    ("CA", "Canada"),
    ("GB", "United Kingdom"),
    ("DE", "Germany"),
    ("FR", "France"),
]

STATUSES = ["active", "inactive", "pending"]

RNG = Random(42)  # noqa: S311 - deterministic test data only


def generate_row(i):
    first = f"User{i}"
    last = f"Test{i}"
    full_name = f"{first} {last}"
    email = f"user{i}@example.com"
    age = RNG.randint(18, 75)
    status = RNG.choice(STATUSES)
    country_code, _ = RNG.choice(COUNTRIES)
    updated_at = (datetime(2024, 1, 1) + timedelta(minutes=i)).isoformat() + "Z"

    # Inject a small fraction of invalid rows for negative coverage
    if i % 50 == 0:
        email = "invalid-email"
    if i % 70 == 0:
        age = 140
    if i % 90 == 0:
        country_code = "ZZ"
    if i % 110 == 0:
        full_name = "SingleName"

    return {
        "full_name": full_name,
        "email": email,
        "age": age,
        "status": status,
        "country_code": country_code,
        "updated_at": updated_at,
    }


def main(rows=1000, out_path="customers_medium.csv"):
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "full_name",
                "email",
                "age",
                "status",
                "country_code",
                "updated_at",
            ],
        )
        writer.writeheader()
        for i in range(rows):
            writer.writerow(generate_row(i))


if __name__ == "__main__":
    main()
