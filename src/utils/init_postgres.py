from src.utils.db import Base, engine
from src.models.expense import Expense  # registers model

def init_db():
    Base.metadata.create_all(bind=engine)
