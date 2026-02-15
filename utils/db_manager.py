import sqlite3
import pandas as pd

DB_PATH = "data/youtube_insight.db"


# Create database and table
def create_database():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            comment TEXT,
            sentiment TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()

    conn.close()


# Insert comments into database
def insert_comments(df):

    conn = sqlite3.connect(DB_PATH)

    df.to_sql("comments", conn, if_exists="append", index=False)

    conn.close()


# Fetch all comments
def fetch_all_comments():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("SELECT * FROM comments", conn)

    conn.close()

    return df


# Run custom SQL query
def run_query(query):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(query, conn)

    conn.close()

    return df