from sql_mapper.model_base import ModelBase
from sql_mapper.sql_executors import SQLiteSQLExecutor
from sql_mapper.string_dump import raw


def test_sql_mapper():

    class A(ModelBase):
        _tablename = "a"
        b: int = "INTEGER"
        c: str = "TEXT"
        _additional_table_lines = "PRIMARY KEY (b)"

    sql_executor = SQLiteSQLExecutor.new(":memory:")
    sql_executor.create_tables(A)

    sql_executor.execute_many("INSERT INTO ?", (
        [A(1, "a")],
        [A(c="b")],
        [A(c="c")]
    ))

    sql_executor.execute(
        "INSERT INTO a VALUES (?, ?)",
        [*A(4, "d").instance_fields.values()]
    )  # Identical to sql_executor.execute("INSERT INTO ?", [A(7, 8)])

    sql_executor.execute("INSERT INTO a VALUES (?, " + raw("'?'") + ")", [5])

    assert list(sql_executor.execute("SELECT * FROM a", model=A)) == [
        A(1, "a"), A(2, "b"), A(3, "c"), A(4, "d"), A(5, "?")
    ]
