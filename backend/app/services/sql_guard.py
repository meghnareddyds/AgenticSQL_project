
import sqlglot
from sqlglot import exp

ALLOWED_FUNCTIONS = {
    "sum",
    "avg",
    "count",
    "min",
    "max",
    "round",
}

ALLOWED_NODES = (
    exp.Select,
    exp.From,
    exp.Table,
    exp.Column,
    exp.Identifier,
    exp.Star,
    exp.Alias,
    exp.Where,
    exp.Group,
    exp.Order,
    exp.Ordered,
    exp.Limit,
    exp.Literal,
    exp.EQ,
    exp.NEQ,
    exp.GT,
    exp.GTE,
    exp.LT,
    exp.LTE,
    exp.And,
    exp.Or,
    exp.Not,
    exp.Is,
    exp.Null,
    exp.Between,
    exp.In,
    exp.Like,
    exp.Paren,
    exp.Add,
    exp.Sub,
    exp.Mul,
    exp.Div,
    exp.Neg,
    exp.Sum,
    exp.Avg,
    exp.Count,
    exp.Min,
    exp.Max,
    exp.Round,
    exp.Distinct,
    exp.Boolean,
)


def validate_sql(sql: str, column_names: list[str]) -> str:
    if not sql or len(sql) > 5000:
        raise ValueError("SQL must be between 1 and 5000 characters")

    try:
        statements = sqlglot.parse(
            sql, read="duckdb"
        )
    except sqlglot.errors.ParseError as exc:
        raise ValueError("Invalid SQL syntax") from exc

    if len(statements) != 1:
        raise ValueError("Exactly one SQL statement is allowed")

    statement = statements[0]

    if not isinstance(statement, exp.Select):
        raise ValueError("Only SELECT statements are allowed")

    tables = list(statement.find_all(exp.Table))
    if len(tables) != 1:
        raise ValueError("Exactly one table is required")

    table = tables[0]
    if (
        table.name.lower() != "sales_data"
        or table.db
        or table.catalog
    ):
        raise ValueError("Only sales_data can be queried")

    allowed_columns = {
        name.lower() for name in column_names
    }

    for node in statement.walk():
        if not isinstance(node, ALLOWED_NODES):
            raise ValueError(
                f"SQL feature not allowed: {type(node).__name__}"
            )

        if isinstance(node, exp.Column):
            if node.name != "*" and (
                node.name.lower() not in allowed_columns
            ):
                # SELECT aliases can appear in ORDER BY.
                aliases = {
                    alias.alias.lower()
                    for alias in statement.expressions
                    if isinstance(alias, exp.Alias)
                }
                if node.name.lower() not in aliases:
                    raise ValueError(
                        f"Unknown column: {node.name}"
                    )

            if node.table and node.table.lower() != "sales_data":
                raise ValueError("Unexpected table qualifier")

        if isinstance(node, exp.Func):
            if node.sql_name().lower() not in ALLOWED_FUNCTIONS:
                raise ValueError(
                    f"Function not allowed: {node.sql_name()}"
                )

    return statement.sql(dialect="duckdb")
