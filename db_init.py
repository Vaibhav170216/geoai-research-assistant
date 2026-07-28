import os
from datetime import datetime

import psycopg

DB_TIMEZONE = datetime.now().astimezone().tzinfo
print(f"Using timezone: {DB_TIMEZONE}")

def get_db_connection():

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "geoai_monitoring"),
        user=os.getenv("POSTGRES_USER", "user"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
    )


def init_db(drop=False):

    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            if drop:
                cur.execute("DROP TABLE IF EXISTS rag_requests")

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS rag_requests (
                    id SERIAL PRIMARY KEY,

                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,

                    application TEXT NOT NULL,

                    model TEXT NOT NULL,
                    instructions TEXT NOT NULL,
                    prompt TEXT NOT NULL,

                    prompt_tokens INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,

                    response_time DOUBLE PRECISION NOT NULL,
                    cost DOUBLE PRECISION NOT NULL,

                    timestamp TIMESTAMPTZ NOT NULL
                )
                """
            )
        conn.commit()

    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("GeoAI monitoring database initialized.")