import pandas as pd
from sqlalchemy import create_engine
from ydata_profiling import ProfileReport
import os

engine = create_engine(os.getenv("GE_DB_CONN_STRING"))
df = pd.read_sql("SELECT * FROM analytics.dim_customers", engine)
profile = ProfileReport(df, title="Customers Profile")
profile.to_file("/opt/airflow/profiling/reports/customers_profile.html")
print("Профиль клиентов сохранён")
