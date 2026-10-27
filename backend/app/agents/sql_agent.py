from typing import Any, TypedDict

from langgraph.graph import StateGraph, START, END

from app.services.database import (
    get_schema,
    execute_readonly_query,
)
from app.services.bedrock_service import generate_sql
from app.services.sql_guard import validate_sql


class SQLAgentState(TypedDict, total=False):
    question: str
    schema_info: dict[str, Any]
    generated_sql: str
    validated_sql: str
    result: dict[str, Any]
    error: str


def load_schema_node(state: SQLAgentState) -> dict:
    """Read the current DuckDB schema."""

    schema_info = get_schema()

    return {
        "schema_info": schema_info,
    }


def generate_sql_node(state: SQLAgentState) -> dict:
    """Ask Amazon Nova Micro to generate SQL."""

    generated_sql = generate_sql(
        question=state["question"],
        schema_info=state["schema_info"],
    )

    return {
        "generated_sql": generated_sql,
    }


def validate_sql_node(state: SQLAgentState) -> dict:
    """Validate generated SQL before execution."""

    columns = [
        column["name"]
        for column in state["schema_info"]["columns"]
    ]

    try:
        validated_sql = validate_sql(
            state["generated_sql"],
            columns,
        )

        return {
            "validated_sql": validated_sql,
            "error": "",
        }

    except ValueError as exc:
        return {
            "error": f"SQL validation failed: {exc}",
        }


def choose_next_step(state: SQLAgentState) -> str:
    """Only execute SQL that passed validation."""

    if state.get("error"):
        return "stop"

    return "execute"


def execute_sql_node(state: SQLAgentState) -> dict:
    """Execute validated SQL using the read-only database service."""

    try:
        result = execute_readonly_query(
            state["validated_sql"]
        )

        return {
            "result": result,
            "error": "",
        }

    except Exception:
        return {
            "error": "SQL execution failed.",
        }


def build_sql_agent():
    workflow = StateGraph(SQLAgentState)

    workflow.add_node("load_schema", load_schema_node)
    workflow.add_node("generate_sql", generate_sql_node)
    workflow.add_node("validate_sql", validate_sql_node)
    workflow.add_node("execute_sql", execute_sql_node)

    workflow.add_edge(START, "load_schema")
    workflow.add_edge("load_schema", "generate_sql")
    workflow.add_edge("generate_sql", "validate_sql")

    workflow.add_conditional_edges(
        "validate_sql",
        choose_next_step,
        {
            "execute": "execute_sql",
            "stop": END,
        },
    )

    workflow.add_edge("execute_sql", END)

    return workflow.compile()


sql_agent = build_sql_agent()


def ask_sql_agent(question: str) -> dict:
    """Run the full natural-language-to-SQL workflow."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    final_state = sql_agent.invoke(
        {
            "question": question,
        }
    )

    return {
        "question": question,
        "sql": final_state.get("validated_sql"),
        "result": final_state.get("result"),
        "error": final_state.get("error") or None,
    }