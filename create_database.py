# create_database.py
# Creates a sample business database for our SQL Agent

import sqlite3
import random
from datetime import datetime, timedelta

# Create database file
conn = sqlite3.connect("business.db")
cursor = conn.cursor()

# ── Create Tables ─────────────────────────────────────────────

# Customers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id          INTEGER PRIMARY KEY,
    name        TEXT,
    email       TEXT,
    city        TEXT,
    country     TEXT,
    joined_date TEXT
)
""")

# Products table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id       INTEGER PRIMARY KEY,
    name     TEXT,
    category TEXT,
    price    REAL,
    stock    INTEGER
)
""")

# Orders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product_id  INTEGER,
    quantity    INTEGER,
    total       REAL,
    order_date  TEXT,
    status      TEXT
)
""")

# ── Insert Sample Data ────────────────────────────────────────

# Customers
cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"]
countries = ["India"]
names = ["Rahul", "Priya", "Amit", "Sneha", "Vijay", "Anita",
         "Ravi", "Deepa", "Kiran", "Pooja", "Sahaji", "Arjun"]

for i in range(1, 101):
    days_ago = random.randint(1, 365)
    joined = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT OR IGNORE INTO customers VALUES (?,?,?,?,?,?)
    """, (
        i,
        random.choice(names) + f" {i}",
        f"user{i}@email.com",
        random.choice(cities),
        "India",
        joined
    ))

# Products
product_data = [
    ("Laptop Pro",      "Electronics",  75000, 50),
    ("Smartphone X",    "Electronics",  25000, 100),
    ("Wireless Earbuds","Electronics",   3500, 200),
    ("Office Chair",    "Furniture",    12000, 30),
    ("Standing Desk",   "Furniture",    25000, 20),
    ("Python Book",     "Books",          800, 150),
    ("AI Handbook",     "Books",         1200, 120),
    ("Coffee Maker",    "Appliances",    4500, 75),
    ("Webcam HD",       "Electronics",   3000, 90),
    ("Mechanical Keyboard", "Electronics", 5000, 60),
]

for i, (name, cat, price, stock) in enumerate(product_data, 1):
    cursor.execute("""
        INSERT OR IGNORE INTO products VALUES (?,?,?,?,?)
    """, (i, name, cat, price, stock))

# Orders
statuses = ["completed", "pending", "cancelled", "shipped"]
for i in range(1, 501):
    days_ago = random.randint(1, 90)
    order_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    qty = random.randint(1, 5)
    product_id = random.randint(1, 10)
    price = product_data[product_id - 1][2]
    cursor.execute("""
        INSERT OR IGNORE INTO orders VALUES (?,?,?,?,?,?,?)
    """, (
        i,
        random.randint(1, 100),
        product_id,
        qty,
        price * qty,
        order_date,
        random.choice(statuses)
    ))

conn.commit()
conn.close()
print("✅ Business database created successfully!")
print("📊 Tables created: customers, products, orders")
print("📦 Sample data: 100 customers, 10 products, 500 orders")

"""

```

Run it:
```
python create_database.py
```

You should see:
```
✅ Business database created successfully!
📊 Tables created: customers, products, orders
📦 Sample data: 100 customers, 10 products, 500 orders
"""