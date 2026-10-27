import os
import re
import boto3
from botocore.exceptions import BotoCoreError, ClientError, ProfileNotFound


AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
AWS_PROFILE = os.getenv("AWS_PROFILE", "agenticsql")
MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "us.amazon.nova-micro-v1:0",
)


def ask_bedrock(question: str) -> str:
    """
    Send a question to Amazon Nova Micro
    and return the generated text.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    try:
        session = boto3.Session(
            profile_name=AWS_PROFILE,
            region_name=AWS_REGION,
        )

        client = session.client("bedrock-runtime")

        response = client.converse(
            modelId=MODEL_ID,
            system=[
                {
                    "text": (
                        "You are AgenticSQL, a helpful SQL and "
                        "data analytics assistant. "
                        "Explain concepts clearly and concisely. "
                        "Do not claim to have executed SQL queries "
                        "or inspected datasets unless you have "
                        "actually done so."
                    )
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": [{"text": question}],
                }
            ],
            inferenceConfig={
                "maxTokens": 150,
                "temperature": 0,
            },
        )

        content = response["output"]["message"]["content"]

        answer = "\n".join(
            block["text"]
            for block in content
            if "text" in block
        )

        return answer or "The model returned an empty response."

    except (ClientError, BotoCoreError, ProfileNotFound) as error:
        raise RuntimeError(
            f"Amazon Bedrock request failed: {error}"
        ) from error


def generate_sql(question: str, schema_info: dict) -> str:
    """
    Generate SQL using the actual DuckDB table schema.

    This function only generates SQL.
    It does not validate or execute it.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    table_name = schema_info["table_name"]
    columns = schema_info["columns"]

    column_descriptions = "\n".join(
        f"- {column['name']}: {column['type']}"
        for column in columns
    )

    prompt = f"""
You are a SQL query generator for DuckDB.

Generate exactly one read-only SELECT query that answers
the user's question.

DATABASE SCHEMA:
Table: {table_name}

Columns:
{column_descriptions}

RULES:
1. Use only the table and columns listed above.
2. Generate DuckDB-compatible SQL.
3. Use SELECT statements only.
4. Do not generate INSERT, UPDATE, DELETE, DROP,
   ALTER, CREATE, COPY, or PRAGMA statements.
5. Do not reference external files, URLs, or databases.
6. Do not invent table names or column names.
7. Return only SQL, without explanations or Markdown.
8. For top-selling products, rank by SUM(quantity).
9. For revenue questions, use the revenue column.
10. Limit detailed row listings to 100 rows.

USER QUESTION:
{question}
"""

    session = boto3.Session(
        profile_name=AWS_PROFILE,
        region_name=AWS_REGION,
    )

    client = session.client("bedrock-runtime")

    response = client.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        inferenceConfig={
            "maxTokens": 300,
            "temperature": 0,
        },
    )

    content = response["output"]["message"]["content"]

    generated_text = "\n".join(
        block["text"]
        for block in content
        if "text" in block
    ).strip()

    # Remove a surrounding Markdown SQL fence if the model adds one.
    generated_text = re.sub(
        r"^```(?:sql)?\s*",
        "",
        generated_text,
        flags=re.IGNORECASE,
    )

    generated_text = re.sub(
        r"\s*```$",
        "",
        generated_text,
    )

    return generated_text.strip()