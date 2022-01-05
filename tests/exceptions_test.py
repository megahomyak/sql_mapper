import pytest

from sql_mapper import ModelBase, exceptions
from sql_mapper.sql_executors import SQLiteSQLExecutor


class A(ModelBase):
    a = "INTEGER"
    b: str = "TEXT"


def test_exceptions():
    sql_executor = SQLiteSQLExecutor.new(":memory:")
    with pytest.raises(exceptions.TablenameNotSpecifiedOnTableCreation) as e:
        sql_executor.create_tables(A)
    assert (
        str(e.value) ==
        "tablename not specified for the model 'A'! You cannot create an "
        "unnamed table!"
    )
    with pytest.raises(exceptions.FieldAlreadyTaken) as e:
        A(1, "abc", a=2)
    assert (
        str(e.value) ==
        "field 'a' was already filled! Check your ordered fields, it may help"
    )
    with pytest.raises(exceptions.TooManyOrderedFields) as e:
        A(1, "abc", 2)
    assert (
        str(e.value) ==
        "model 'A' has 2 fields, but 3 ordered fields was given"
    )
    with pytest.raises(exceptions.UnknownField) as e:
        A(c=1)
    assert (
        str(e.value) ==
        "unknown field 'c'! (It is not declared in the model)"
    )
    with pytest.raises(exceptions.TablenameNotSpecifiedOnInsertion) as e:
        sql_executor.execute("INSERT INTO ?", [A(1, "abc")])
    assert (
        str(e.value) ==
        "tablename not specified for the model 'A'! SQL mapper "
        "doesn't know what tablename to use in query parameter mark "
        "substitution, so add the tablename to the model!"
    )
