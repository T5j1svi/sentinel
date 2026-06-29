from __future__ import annotations
import sqlite3
from pathlib import Path
import pandas as pd
from .utils import safe_filename

DB_PATH = Path("database/propaganda_detector.db")


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        mode TEXT,
        input_value TEXT,
        notes TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_name TEXT,
        section TEXT,
        platform TEXT,
        handle TEXT,
        role TEXT,
        confidence TEXT,
        similarity_score REAL,
        title TEXT,
        snippet TEXT,
        url TEXT,
        thumbnail_url TEXT,
        query_label TEXT,
        query_language TEXT,
        search_stage TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    con.commit(); con.close()


def save_case(case_name: str, mode: str, input_value: str, df: pd.DataFrame):
    init_db()
    con = sqlite3.connect(DB_PATH)
    con.execute("INSERT INTO cases(case_name, mode, input_value, notes) VALUES(?,?,?,?)", (case_name, mode, input_value, "saved from GUI"))
    if df is not None and not df.empty:
        cols = ["section", "platform", "handle", "role", "confidence", "similarity_score", "title", "snippet", "url", "thumbnail_url", "query_label", "query_language", "search_stage"]
        x = df.copy()
        for c in cols:
            if c not in x.columns:
                x[c] = ""
        x["case_name"] = case_name
        x[["case_name"] + cols].to_sql("results", con, if_exists="append", index=False)
    con.commit(); con.close()


def export_csv(case_name: str, df: pd.DataFrame) -> str:
    Path("exports").mkdir(exist_ok=True)
    path = Path("exports") / f"{safe_filename(case_name)}_results.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return str(path)
