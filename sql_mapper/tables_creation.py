from typing import Type

from sql_mapper.abstract_sql_executor import (
    AbstractSQLExecutor, AbstractAsyncSQLExecutor
)
from sql_mapper.model_base import ModelBase


def create_tables(sql_executor: AbstractSQLExecutor, *tables: Type[ModelBase]):
    for table in tables:
        sql_executor.execute(table.get_table_creation_sql())
    sql_executor.commit()


async def create_tables_async(
        sql_executor: AbstractAsyncSQLExecutor, *tables: Type[ModelBase]):
    for table in tables:
        await sql_executor.execute(table.get_table_creation_sql())
    await sql_executor.commit()
