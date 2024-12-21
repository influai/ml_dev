import os
import time

import polars as pl
from pathlib import Path
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

SCHEME = "parse"
TABLE = "channels"
COLUMNS = ["id", "title", "about", "last_pinned_msg_id"]
TO_FILE = Path("/home/deniskirbaba/Documents/influai-data/channels_data_for_emd.csv")

try:
    rows = []
    with conn.cursor() as cursor:
        rows_fetched = 0
        start_time = time.time()

        for row in tqdm(
            cursor.stream(f"SELECT {', '.join(COLUMNS)} FROM {SCHEME}.{TABLE};"), leave=False
        ):
            rows_fetched += 1
            rows += [row]
            if rows_fetched % 10_000 == 0:
                elapsed_time = time.time() - start_time
                print(f"Time spent: {elapsed_time:.2f} seconds, Rows fetched: {rows_fetched}")

        elapsed_time = time.time() - start_time
        print(f"\nFinal results:")
        print(f"Total time: {elapsed_time:.2f} seconds")
        print(f"Total rows fetched: {rows_fetched}")

        print(f"Saving to {TO_FILE}")
        df = pl.DataFrame(rows, schema=COLUMNS, orient="row")
        df.write_csv(TO_FILE)


except Exception as e:
    print(f"Error during data fetching: {e}")
    raise
finally:
    conn.close()
    print("Connection closed.")
