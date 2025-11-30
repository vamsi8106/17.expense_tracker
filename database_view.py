import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg://db_user:db_pass@34.230.77.137:5432/mydb"

engine = create_engine(DATABASE_URL)

TABLE_NAME = "expenses"

query = f"""
    SELECT * FROM {TABLE_NAME}
    ORDER BY ctid DESC
    LIMIT 20;
"""

df = pd.read_sql(query, engine)

print("\n===== Recent DB Entries =====")
print(df)

