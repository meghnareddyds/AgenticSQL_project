from app.services.database import get_schema
from app.services.bedrock_service import generate_sql


def main():
    schema_info = get_schema()

    print("Table:", schema_info["table_name"])
    print("Rows:", schema_info["row_count"])

    question = "Give me the top 5 sold products"

    print("\nQuestion:", question)

    generated_sql = generate_sql(
        question=question,
        schema_info=schema_info,
    )

    print("\nGenerated SQL:")
    print(generated_sql)


if __name__ == "__main__":
    main()