
from pathlib import Path
from threading import Lock

import duckdb

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "agenticsql.duckdb"
TABLE_NAME = "sales_data"

# Prevent uploads and queries from changing the database
# simultaneously within this single backend process.
DB_LOCK = Lock()


def initialize_database():
    with duckdb.connect(str(DB_PATH)) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS sales_data (
                order_id INTEGER,
                order_date DATE,
                product VARCHAR,
                category VARCHAR,
                region VARCHAR,
                quantity INTEGER,
                unit_price DOUBLE,
                revenue DOUBLE
            )
            """
        )


def replace_dataset(csv_path: Path):
    # CSV ingestion is performed only on a trusted temporary
    # file written by our own upload endpoint.
    with DB_LOCK:
        with duckdb.connect(str(DB_PATH)) as con:
            con.execute("BEGIN TRANSACTION")
            try:
                con.execute(
                    "CREATE OR REPLACE TABLE staging_upload "
                    "AS SELECT * FROM read_csv_auto(?)",
                    [str(csv_path)],
                )

                columns = con.execute(
                    "DESCRIBE staging_upload"
                ).fetchall()

                if not columns:
                    raise ValueError("CSV contains no columns")

                if len(columns) > 100:
                    raise ValueError(
                        "CSV exceeds the 100-column limit"
                    )

                con.execute(
                    "CREATE OR REPLACE TABLE sales_data "
                    "AS SELECT * FROM staging_upload"
                )
                con.execute("DROP TABLE staging_upload")
                con.execute("COMMIT")
            except Exception:
                con.execute("ROLLBACK")
                raise


def get_schema():
    with DB_LOCK:
        with duckdb.connect(
            str(DB_PATH), read_only=True
        ) as con:
            columns = con.execute(
                "DESCRIBE sales_data"
            ).fetchall()

            count = con.execute(
                "SELECT COUNT(*) FROM sales_data"
            ).fetchone()[0]

    return {
        "table_name": TABLE_NAME,
        "row_count": count,
        "columns": [
            {"name": row[0], "type": row[1]}
            for row in columns
        ],
    }


def execute_readonly_query(sql: str):
    # Validate SQL before calling this function.
    # External file and extension access is disabled.
    with DB_LOCK:
        with duckdb.connect(
            str(DB_PATH),
            read_only=True,
            config={"enable_external_access": "false"},
        ) as con:
            # A hard upper bound on returned rows.
            cursor = con.execute(
                f"SELECT * FROM ({sql}) AS result LIMIT 100"
            )

            column_names = [
                column[0]
                for column in cursor.description
            ]
            rows = cursor.fetchall()

    return {
        "columns": column_names,
        "rows": [
            [
                value.isoformat()
                if hasattr(value, "isoformat")
                else str(value)
                if not isinstance(
                    value, (str, int, float, bool, type(None))
                )
                else value
                for value in row
            ]
            for row in rows
        ],
        "row_count": len(rows),
        "truncated": len(rows) == 100,
    }
