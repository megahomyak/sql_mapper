import sqlite3
from typing import Sequence, Iterable

from sql_mapper.abstract_sql_executor import AbstractSQLExecutor


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
