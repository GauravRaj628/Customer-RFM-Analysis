"""
src/database.py — SQLite persistence and query engine.
Customer RFM Analysis

Provides SQLite integration to record analysis execution runs,
persist customer RFM scores, and archive segment performance summaries.
All database operations utilize parameterized SQL queries.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any
import pandas as pd

from src.config import DATABASE_PATH


def get_connection(db_path: str | Path = DATABASE_PATH) -> sqlite3.Connection:
    """
    Open or create an SQLite database connection.

    Parameters
    ----------
    db_path : str | Path
        Filesystem path to the SQLite database file, or ':memory:'.

    Returns
    -------
    sqlite3.Connection
    """
    if str(db_path) != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """
    Initialize database schema with analysis_runs, rfm_results, and segment_summary tables.

    Parameters
    ----------
    conn : sqlite3.Connection
        Active SQLite database connection.
    """
    cursor = conn.cursor()

    # 1. analysis_runs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_timestamp TEXT NOT NULL,
            reference_date TEXT NOT NULL,
            total_transactions INTEGER NOT NULL,
            valid_transactions INTEGER NOT NULL,
            total_customers INTEGER NOT NULL,
            total_revenue REAL NOT NULL,
            notes TEXT
        );
    """)

    # 2. rfm_results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rfm_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            customer_id TEXT NOT NULL,
            customer_name TEXT,
            recency_days INTEGER NOT NULL,
            frequency INTEGER NOT NULL,
            monetary REAL NOT NULL,
            r_score INTEGER NOT NULL,
            f_score INTEGER NOT NULL,
            m_score INTEGER NOT NULL,
            rfm_score INTEGER NOT NULL,
            rfm_cell TEXT NOT NULL,
            activity_band TEXT NOT NULL,
            customer_segment TEXT NOT NULL,
            FOREIGN KEY (run_id) REFERENCES analysis_runs (run_id)
        );
    """)

    # 3. segment_summary table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS segment_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            customer_segment TEXT NOT NULL,
            customer_count INTEGER NOT NULL,
            customer_percentage REAL NOT NULL,
            total_revenue REAL NOT NULL,
            revenue_percentage REAL NOT NULL,
            avg_recency REAL NOT NULL,
            avg_frequency REAL NOT NULL,
            avg_monetary REAL NOT NULL,
            avg_rfm_score REAL NOT NULL,
            FOREIGN KEY (run_id) REFERENCES analysis_runs (run_id)
        );
    """)

    conn.commit()


def log_analysis_run(
    conn: sqlite3.Connection,
    reference_date: str,
    total_transactions: int,
    valid_transactions: int,
    total_customers: int,
    total_revenue: float,
    notes: str = "",
) -> int:
    """
    Record an execution run entry in analysis_runs table using parameterized query.

    Returns
    -------
    int
        Generated run_id primary key.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO analysis_runs (
            run_timestamp, reference_date, total_transactions,
            valid_transactions, total_customers, total_revenue, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            str(reference_date),
            int(total_transactions),
            int(valid_transactions),
            int(total_customers),
            float(round(total_revenue, 2)),
            str(notes),
        ),
    )
    conn.commit()
    return int(cursor.lastrowid)


def save_rfm_results(
    conn: sqlite3.Connection,
    rfm_df: pd.DataFrame,
    run_id: int | None = None,
) -> None:
    """
    Bulk insert customer RFM scores into rfm_results table using parameterized queries.

    Parameters
    ----------
    conn : sqlite3.Connection
        Active database connection.
    rfm_df : pd.DataFrame
        Scored and segmented RFM DataFrame.
    run_id : int | None
        Associated run ID. If None, attaches to the latest run.
    """
    if rfm_df.empty:
        return

    cursor = conn.cursor()
    if run_id is None:
        cursor.execute("SELECT MAX(run_id) FROM analysis_runs;")
        row = cursor.fetchone()
        run_id = row[0] if (row and row[0] is not None) else 1

    records = []
    for _, row in rfm_df.iterrows():
        records.append((
            int(run_id),
            str(row["customer_id"]),
            str(row.get("customer_name", "")),
            int(row["recency_days"]),
            int(row["frequency"]),
            float(row["monetary"]),
            int(row.get("r_score", 3)),
            int(row.get("f_score", 3)),
            int(row.get("m_score", 3)),
            int(row.get("rfm_score", 9)),
            str(row.get("rfm_cell", "333")),
            str(row.get("activity_band", "Recent")),
            str(row.get("customer_segment", "Loyal Customers")),
        ))

    cursor.executemany(
        """
        INSERT INTO rfm_results (
            run_id, customer_id, customer_name, recency_days, frequency,
            monetary, r_score, f_score, m_score, rfm_score, rfm_cell,
            activity_band, customer_segment
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        records,
    )
    conn.commit()


def load_rfm_results(
    conn: sqlite3.Connection,
    run_id: int | None = None,
) -> pd.DataFrame:
    """
    Load RFM records from SQLite using parameterized SELECT query.

    Parameters
    ----------
    conn : sqlite3.Connection
        Active database connection.
    run_id : int | None
        Target run ID. If None, queries the most recent run.

    Returns
    -------
    pd.DataFrame
    """
    if run_id is None:
        query = """
            SELECT customer_id, customer_name, recency_days, frequency,
                   monetary, r_score, f_score, m_score, rfm_score,
                   rfm_cell, activity_band, customer_segment
            FROM rfm_results
            WHERE run_id = (SELECT MAX(run_id) FROM analysis_runs)
            ORDER BY rfm_score DESC;
        """
        return pd.read_sql_query(query, conn)
    else:
        query = """
            SELECT customer_id, customer_name, recency_days, frequency,
                   monetary, r_score, f_score, m_score, rfm_score,
                   rfm_cell, activity_band, customer_segment
            FROM rfm_results
            WHERE run_id = ?
            ORDER BY rfm_score DESC;
        """
        return pd.read_sql_query(query, conn, params=[int(run_id)])


def save_segment_summary(
    conn: sqlite3.Connection,
    segment_df: pd.DataFrame,
    run_id: int | None = None,
) -> None:
    """
    Save segment overview summary into segment_summary table.

    Parameters
    ----------
    conn : sqlite3.Connection
        Active database connection.
    segment_df : pd.DataFrame
        Segment summary DataFrame.
    run_id : int | None
        Associated run ID. If None, attaches to the latest run.
    """
    if segment_df.empty:
        return

    cursor = conn.cursor()
    if run_id is None:
        cursor.execute("SELECT MAX(run_id) FROM analysis_runs;")
        row = cursor.fetchone()
        run_id = row[0] if (row and row[0] is not None) else 1

    records = []
    for _, row in segment_df.iterrows():
        records.append((
            int(run_id),
            str(row["customer_segment"]),
            int(row["customer_count"]),
            float(row["customer_percentage"]),
            float(row["total_revenue"]),
            float(row["revenue_percentage"]),
            float(row["avg_recency"]),
            float(row["avg_frequency"]),
            float(row["avg_monetary"]),
            float(row["avg_rfm_score"]),
        ))

    cursor.executemany(
        """
        INSERT INTO segment_summary (
            run_id, customer_segment, customer_count, customer_percentage,
            total_revenue, revenue_percentage, avg_recency, avg_frequency,
            avg_monetary, avg_rfm_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        records,
    )
    conn.commit()


def load_segment_summary(
    conn: sqlite3.Connection,
    run_id: int | None = None,
) -> pd.DataFrame:
    """
    Retrieve segment summary overview from SQLite using parameterized query.

    Parameters
    ----------
    conn : sqlite3.Connection
        Active database connection.
    run_id : int | None
        Target run ID. If None, queries the most recent run.

    Returns
    -------
    pd.DataFrame
    """
    if run_id is None:
        query = """
            SELECT customer_segment, customer_count, customer_percentage,
                   total_revenue, revenue_percentage, avg_recency,
                   avg_frequency, avg_monetary, avg_rfm_score
            FROM segment_summary
            WHERE run_id = (SELECT MAX(run_id) FROM analysis_runs);
        """
        return pd.read_sql_query(query, conn)
    else:
        query = """
            SELECT customer_segment, customer_count, customer_percentage,
                   total_revenue, revenue_percentage, avg_recency,
                   avg_frequency, avg_monetary, avg_rfm_score
            FROM segment_summary
            WHERE run_id = ?;
        """
        return pd.read_sql_query(query, conn, params=[int(run_id)])


def list_analysis_runs(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Retrieve all historical analysis execution runs ordered by most recent first.

    Returns
    -------
    pd.DataFrame
    """
    query = """
        SELECT run_id, run_timestamp, reference_date, total_transactions,
               valid_transactions, total_customers, total_revenue, notes
        FROM analysis_runs
        ORDER BY run_id DESC;
    """
    return pd.read_sql_query(query, conn)
