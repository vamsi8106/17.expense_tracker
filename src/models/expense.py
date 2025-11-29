from sqlalchemy import Column, Integer, String, Numeric, Date
from src.utils.db import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, index=True)       # 👈 changed
    amount = Column(Numeric, nullable=False)
    category = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=True)
