#!/usr/bin/env python3
#src/mcp_servers/expense_tracker.py
import sys, os

# Allow imports from src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from mcp.server.fastmcp import FastMCP
from src.utils.db import initialize_db, get_connection
from src.utils.date_parser import parse_natural_date
from src.utils.logger import get_logger
from src.utils.metrics import EXPENSES_ADDED, MCP_TOOL_CALLS


logger = get_logger("MCP-Expenses")
mcp = FastMCP("expenses")

# Uniform categories
CATEGORIES = {
    "food", "travel", "groceries", "shopping", "medicine",
    "bills", "rent", "entertainment", "misc"
}

# Initialize DB once
initialize_db()


# --------------------------------------------------------
# 📌 ADD EXPENSE
# --------------------------------------------------------
@mcp.tool()
async def add_expense(
    user: str,
    amount: float,
    category: str,
    date: str,
    description: str = ""
):
    """
    Add an expense entry for a user.
    """

    logger.info(f"[ADD] User={user} Amount={amount} Category={category}")

    # Metrics
    EXPENSES_ADDED.inc()
    MCP_TOOL_CALLS.inc()

    # Normalize input
    category = category.lower().strip()
    if category not in CATEGORIES:
        return {
            "status": "error",
            "message": f"Invalid category '{category}'. Allowed: {', '.join(sorted(CATEGORIES))}"
        }

    # Parse natural date ("yesterday", "last Monday", etc.)
    parsed_date = parse_natural_date(date)
    if parsed_date:
        date = parsed_date

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO expenses (user, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user, amount, category, date, description),
        )
        conn.commit()
        conn.close()

        logger.info(f"[ADD SUCCESS] {user} spent {amount} on {category}")

        return {
            "status": "ok",
            "message": f"Expense added for {user}",
            "data": {
                "user": user,
                "amount": amount,
                "category": category,
                "date": date,
                "description": description
            }
        }

    except Exception as e:
        logger.error(f"DB error while adding expense: {e}")
        return {"status": "error", "message": str(e)}


# --------------------------------------------------------
# 📌 LIST EXPENSES
# --------------------------------------------------------
@mcp.tool()
async def list_expenses(user: str):
    """
    List all expenses for a user.
    """

    MCP_TOOL_CALLS.inc()
    logger.info(f"[LIST] Fetching all expenses for {user}")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT amount, category, date, description
            FROM expenses
            WHERE user = ?
            ORDER BY date DESC
            """,
            (user,),
        )

        rows = cur.fetchall()
        conn.close()

        return {
            "status": "ok",
            "user": user,
            "count": len(rows),
            "expenses": [
                {
                    "amount": r[0],
                    "category": r[1],
                    "date": r[2],
                    "description": r[3],
                }
                for r in rows
            ],
        }

    except Exception as e:
        logger.error(f"DB error in list_expenses: {e}")
        return {"status": "error", "message": str(e)}


# --------------------------------------------------------
# 📌 EXPENSES BETWEEN DATES
# --------------------------------------------------------
@mcp.tool()
async def expenses_between(user: str, start_date: str, end_date: str):
    """
    Get expenses between two dates for a user.
    """

    MCP_TOOL_CALLS.inc()
    logger.info(f"[BETWEEN] {user} from {start_date} to {end_date}")

    s = parse_natural_date(start_date) or start_date
    e = parse_natural_date(end_date) or end_date

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT amount, category, date, description
            FROM expenses
            WHERE user = ? AND date BETWEEN ? AND ?
            ORDER BY date DESC
            """,
            (user, s, e),
        )

        rows = cur.fetchall()
        conn.close()

        return {
            "status": "ok",
            "user": user,
            "from": s,
            "to": e,
            "count": len(rows),
            "expenses": [
                {
                    "amount": r[0],
                    "category": r[1],
                    "date": r[2],
                    "description": r[3],
                }
                for r in rows
            ],
        }

    except Exception as e:
        logger.error(f"DB error in expenses_between: {e}")
        return {"status": "error", "message": str(e)}


# --------------------------------------------------------
# 📌 CATEGORY SUMMARY
# --------------------------------------------------------
@mcp.tool()
async def category_summary(user: str):
    """
    Summarize spending per category.
    """

    MCP_TOOL_CALLS.inc()
    logger.info(f"[SUMMARY] Category spend for {user}")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT category, SUM(amount)
            FROM expenses
            WHERE user = ?
            GROUP BY category
            """,
            (user,),
        )

        rows = cur.fetchall()
        conn.close()

        return {
            "status": "ok",
            "user": user,
            "summary": {cat: total for cat, total in rows},
        }

    except Exception as e:
        logger.error(f"DB error in category_summary: {e}")
        return {"status": "error", "message": str(e)}


# --------------------------------------------------------
# SERVER ENTRYPOINT
# --------------------------------------------------------
def main():
    logger.info("Starting MCP Expense Server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
