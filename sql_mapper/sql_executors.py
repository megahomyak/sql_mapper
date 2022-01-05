import sqlite3
from typing import Sequence, Iterable, Type

from sql_mapper import exceptions
from sql_mapper.abstract_sql_executor import AbstractSQLExecutor
from sql_mapper.model_base import ModelBase


class SQLiteSQLExecutor(AbstractSQLExecutor):
    new_parameter_mark = "?"

    def _execute_sql_statement(
            self, statement: str, parameters: list) -> Iterable[Sequence]:
        return self.cursor.execute(statement, parameters)

    def __init__(
            self, connection: sqlite3.Connection,
            cursor: sqlite3.Cursor):
        self.connection = connection
        self.cursor = cursor

    def commit(self):
        self.connection.commit()

    @classmethod
    def new(cls, file_path: str):
        connection = sqlite3.connect(file_path)
        return cls(connection, connection.cursor())

    def create_tables(self, *tables: Type[ModelBase]):
        for table in tables:
            table_data = table.get_table_data()
            if not table_data.name:
                raise exceptions.TablenameNotSpecifiedOnTableCreation(
                    model_name=table.__name__
                )
            sql_statement = (
                f"CREATE TABLE IF NOT EXISTS {table_data.name} ("
                + ",".join(
                    f"{field_name} {field_value}"
                    for field_name, field_value in table_data.fields.items()
                )
                + (
                    f",{table_data.additional_table_lines}"
                    if table_data.additional_table_lines else
                    ""
                ) + ")"
            )
            self.cursor.execute(sql_statement)
