#!/usr/bin/env python3
import sys, os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from mcp.server.fastmcp import FastMCP
from sqlalchemy import text
from src.utils.db import SessionLocal
from src.utils.init_postgres import init_db
from src.utils.date_parser import parse_natural_date
from src.utils.logger import get_logger
from src.utils.metrics import EXPENSES_ADDED, MCP_TOOL_CALLS

logger = get_logger("MCP-Expenses")
mcp = FastMCP("expenses")

CATEGORIES = {
    "food", "travel", "groceries", "shopping", "medicine",
    "bills", "rent", "entertainment", "misc"
}

# Initialize schema
init_db()


# -----------------------------------------------------
# ADD EXPENSE
# -----------------------------------------------------
@mcp.tool()
async def add_expense(
    user: str,
    amount: float,
    category: str,
    date: str,
    description: str = ""
):
    MCP_TOOL_CALLS.inc()
    EXPENSES_ADDED.inc()

    category = category.lower().strip()
    if category not in CATEGORIES:
        return {"status": "error", "message": f"Invalid category '{category}'"}

    parsed = parse_natural_date(date)
    date = parsed or date

    db = SessionLocal()
    try:
        db.execute(
            text("""
                INSERT INTO expenses (username, amount, category, date, description)
                VALUES (:username, :amount, :category, :date, :description)
            """),
            {
                "username": user,
                "amount": amount,
                "category": category,
                "date": date,
                "description": description,
            }
        )
        db.commit()

        return {"status": "ok", "message": "Expense added"}
    except Exception as e:
        db.rollback()
        logger.error(f"DB error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


# -----------------------------------------------------
# LIST EXPENSES
# -----------------------------------------------------
@mcp.tool()
async def list_expenses(user: str):
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT amount, category, date, description
                FROM expenses
                WHERE username = :username
                ORDER BY date DESC
            """),
            {"username": user}
        ).fetchall()

        return {
            "status": "ok",
            "user": user,
            "count": len(rows),
            "expenses": [
                {
                    "amount": float(r[0]),
                    "category": r[1],
                    "date": r[2].strftime("%Y-%m-%d"),
                    "description": r[3],
                }
                for r in rows
            ],
        }
    finally:
        db.close()


# -----------------------------------------------------
# BETWEEN DATES
# -----------------------------------------------------
@mcp.tool()
async def expenses_between(user: str, start_date: str, end_date: str):
    s = parse_natural_date(start_date) or start_date
    e = parse_natural_date(end_date) or end_date

    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT amount, category, date, description
                FROM expenses
                WHERE username = :username
                  AND date BETWEEN :s AND :e
                ORDER BY date DESC
            """),
            {"username": user, "s": s, "e": e}
        ).fetchall()

        return {
            "status": "ok",
            "user": user,
            "from": s,
            "to": e,
            "count": len(rows),
            "expenses": [
                {
                    "amount": float(r[0]),
                    "category": r[1],
                    "date": r[2].strftime("%Y-%m-%d"),
                    "description": r[3],
                }
                for r in rows
            ],
        }
    finally:
        db.close()


# -----------------------------------------------------
# CATEGORY SUMMARY
# -----------------------------------------------------
@mcp.tool()
async def category_summary(user: str):
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT category, SUM(amount)
                FROM expenses
                WHERE username = :username
                GROUP BY category
            """),
            {"username": user}
        ).fetchall()

        return {
            "status": "ok",
            "user": user,
            "summary": {r[0]: float(r[1]) for r in rows},
        }
    finally:
        db.close()


def main():
    logger.info("Starting MCP Expense Server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
