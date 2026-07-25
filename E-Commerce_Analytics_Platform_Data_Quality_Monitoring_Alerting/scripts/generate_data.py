import os
import random
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine
from faker import Faker

fake = Faker()
engine = create_engine(
    f"postgresql://{os.getenv('DBT_USER')}:{os.getenv('DBT_PASSWORD')}@"
    f"{os.getenv('DBT_HOST')}:{os.getenv('DBT_PORT')}/{os.getenv('DBT_DB')}"
)

def generate_orders(n=10000):
    orders = []
    for _ in range(n):
        orders.append({
            "order_id": fake.uuid4()[:8],
            "customer_id": fake.uuid4()[:8],
            "order_date": fake.date_time_between(start_date="-1y"),
            "status": random.choice(["pending", "shipped", "delivered", "cancelled"]),
            "total_amount": round(random.uniform(10, 5000), 2)
        })
    return pd.DataFrame(orders)

def generate_order_items(orders_df):
    items = []
    for _, row in orders_df.iterrows():
        for _ in range(random.randint(1, 5)):
            items.append({
                "item_id": fake.uuid4()[:8],
                "order_id": row["order_id"],
                "product_id": fake.uuid4()[:8],
                "quantity": random.randint(1, 10),
                "unit_price": round(random.uniform(5, 200), 2)
            })
    return pd.DataFrame(items)

if __name__ == "__main__":
    orders = generate_orders()
    items = generate_order_items(orders)

    with engine.begin() as conn:
        orders.to_sql("orders", conn, schema="raw", if_exists="replace", index=False)
        items.to_sql("order_items", conn, schema="raw", if_exists="replace", index=False)
    print(" Данные загружены в raw.orders и raw.order_items")
