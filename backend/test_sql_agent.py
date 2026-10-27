import json

from app.agents.sql_agent import ask_sql_agent


def main():
    question = "Give me the top 5 sold products"

    print("Question:", question)

    response = ask_sql_agent(question)

    print("\nAgent response:")
    print(
        json.dumps(
            response,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()