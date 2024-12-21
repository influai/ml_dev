import os
import time

import polars as pl
import psycopg
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

try:
    conn = psycopg.connect(
        host=os.getenv("DB_IP"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
    )
    print("Connection established.")
except Exception as e:
    print(f"Error connecting to the database: {e}")
    raise


def save(rows, file_name):
    print(f"\nSaving to {file_name}")
    df = pl.DataFrame(rows, schema=COLUMNS, orient="row")
    df.write_csv(file_name)


SCHEME = "parse"
TABLE = "posts_metadata"
COLUMNS = ["id", "channel_id", "post_date"]
# TO_FILE = Path("/home/deniskirbaba/Documents/influai-data/embeddings/posts_meta.csv")

# QUERY = "SELECT id FROM parse.posts_content WHERE raw_text IS NOT NULL AND raw_text <> '';"
QUERY = f"SELECT {', '.join(COLUMNS)} FROM {SCHEME}.{TABLE};"

try:
    rows = []
    with conn.cursor() as cursor:
        rows_fetched = 0
        start_time = time.time()

        for row in tqdm(cursor.stream(QUERY), leave=False):
            rows_fetched += 1
            rows += [row]

            if rows_fetched % 5_000_000 == 0:
                save(
                    rows,
                    f"/home/deniskirbaba/Documents/influai-data/embeddings/posts_meta_{rows_fetched}.csv",
                )
                rows = []

    save(
        rows, f"/home/deniskirbaba/Documents/influai-data/embeddings/posts_meta_{rows_fetched}.csv"
    )

except Exception as e:
    print(f"Error during data fetching: {e}")
    raise
finally:
    conn.close()
    print("Connection closed.")

print(f"\nTotal rows fetched: {rows_fetched}")
