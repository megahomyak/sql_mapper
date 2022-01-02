from sql_mapper.model_base import ModelBase
from sql_mapper.sql_executors import SQLiteSQLExecutor
from sql_mapper.tables_creation import create_tables


def test_sql_mapper():

    class A(ModelBase):
        _tablename = "a"
        b: int = "INTEGER"
        c: str = "TEXT"
        _additional_table_lines = "PRIMARY KEY (b)"

    sql_executor = SQLiteSQLExecutor.new(":memory:")
    create_tables(sql_executor, A)

    sql_executor.execute_many("INSERT INTO a VALUES ?", (
        [A(1, "a")],
        [A(2, "b")],
        [A(3, "c")]
    ))

    sql_executor.execute(
        "INSERT INTO a VALUES (?, ?)",
        [*A(4, "d").values()]
    )  # Identical to sql_executor.execute("INSERT INTO a VALUES ?", A(7, 8))

    assert list(sql_executor.execute("SELECT * FROM a", model=A)) == [
        A(1, "a"), A(2, "b"), A(3, "c"), A(4, "d")
    ]
