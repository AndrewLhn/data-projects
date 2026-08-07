import os
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from faker import Faker

fake = Faker()
engine = create_engine(os.getenv('DBT_DB_CONN'))

def generate_customers(n=100000):
    customers = []
    for i in range(n):
        customers.append({
            'customer_id': fake.uuid4()[:8],
            'email': fake.email(),
            'signup_date': fake.date_time_between(start_date="-3y"),
            'country': fake.country(),
            'city': fake.city(),
            'age': random.randint(18, 70)
        })
    return pd.DataFrame(customers)

def generate_products():
    categories = ['Electronics', 'Clothing', 'Home', 'Books', 'Sports', 'Toys', 'Food']
    products = []
    for i in range(5000):
        products.append({
            'product_id': fake.uuid4()[:8],
            'product_name': fake.catch_phrase(),
            'category': random.choice(categories),
            'price': round(random.uniform(5, 500), 2)
        })
    return pd.DataFrame(products)

def generate_orders(customers, start_date='-2y', end_date='today', n=1_000_000):
    orders = []
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    for _ in range(n):
        customer = random.choice(customers['customer_id'].values)
        order_date = fake.date_time_between(start_date=start, end_date=end)
        orders.append({
            'order_id': fake.uuid4()[:8],
            'customer_id': customer,
            'order_date': order_date,
            'status': random.choice(['pending', 'shipped', 'delivered', 'cancelled'])
        })
    return pd.DataFrame(orders)

def generate_order_items(orders, products, max_items=8):
    items = []
    for _, order in orders.iterrows():
        n_items = random.randint(1, max_items)
        for _ in range(n_items):
            product = random.choice(products['product_id'].values)
            qty = random.randint(1, 5)
            price = products[products['product_id'] == product]['price'].values[0]
            items.append({
                'item_id': fake.uuid4()[:8],
                'order_id': order['order_id'],
                'product_id': product,
                'quantity': qty,
                'unit_price': price,
                'total_price': qty * price
            })
    return pd.DataFrame(items)

def generate_events(customers, n=500_000):
    event_types = ['view', 'add_to_cart', 'remove_from_cart', 'purchase']
    pages = ['home', 'product', 'category', 'cart', 'checkout', 'profile']
    events = []
    for _ in range(n):
        customer = random.choice(customers['customer_id'].values)
        events.append({
            'event_id': fake.uuid4()[:8],
            'customer_id': customer,
            'event_type': random.choice(event_types),
            'page': random.choice(pages),
            'timestamp': fake.date_time_between(start_date="-1y"),
            'product_id': None if random.random() > 0.7 else fake.uuid4()[:8],
            'price': None if random.random() > 0.8 else round(random.uniform(5, 500), 2)
        })
    return pd.DataFrame(events)

if __name__ == "__main__":
    print("Генерация клиентов...")
    customers = generate_customers(100000)
    print("Генерация товаров...")
    products = generate_products()
    print("Генерация заказов (1 млн)...")
    orders = generate_orders(customers, n=1_000_000)
    print("Генерация позиций заказов (~5 млн)...")
    items = generate_order_items(orders, products)
    print("Генерация событий (500 тыс)...")
    events = generate_events(customers, n=500_000)
    
    with engine.begin() as conn:
        customers.to_sql('customers', conn, schema='raw', if_exists='replace', index=False, chunksize=10000)
        products.to_sql('products', conn, schema='raw', if_exists='replace', index=False, chunksize=10000)
        orders.to_sql('orders', conn, schema='raw', if_exists='replace', index=False, chunksize=10000)
        items.to_sql('order_items', conn, schema='raw', if_exists='replace', index=False, chunksize=10000)
        events.to_sql('events', conn, schema='raw', if_exists='replace', index=False, chunksize=10000)
    
