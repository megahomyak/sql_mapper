import re
from abc import ABC, abstractmethod
from typing import (
    Iterable, Optional, Type, TypeVar, Union, Sequence, AsyncIterable
)

from sql_mapper.model_base import ModelBase
from sql_mapper.string_dump import (
    StringDump, FormattableString, QUESTION_MARK_PATTERN,
    NewQueryStringWithArguments
)

GenericModel = TypeVar("GenericModel", bound=ModelBase)
MaybeModel = Optional[Type[GenericModel]]


class AbstractSQLExecutor(ABC):
    new_parameter_mark: str
    old_parameter_mark: re.Pattern = QUESTION_MARK_PATTERN

    def _prepare_query_and_arguments(
            self, sql_statement: str, parameters: Iterable
    ) -> NewQueryStringWithArguments:
        if isinstance(sql_statement, str):
            string_dump = StringDump()
            string_dump.strings.append(FormattableString(sql_statement))
            sql_statement = string_dump
        return sql_statement.reformat_collected_query(
            old_arguments=parameters,
            new_parameter_mark=self.new_parameter_mark,
            old_parameter_mark=self.old_parameter_mark
        )

    def execute(
            self, sql_statement: Union[str, StringDump],
            parameters: Iterable = (), model: MaybeModel = None
    ) -> Iterable[Union[Sequence, GenericModel]]:
        """
        sql_statement's parameter marks will be ?, if not overridden
        (.old_parameter_mark attribute). Every instance of ModelBase's
        inherited class will alter the sql_statement, so instead of question
        mark it will have a sequence of question marks, their amount will be
        equal to the amount of members of passed model (in parameters, not in
        model=)

        This function should NOT be a generator!!! It should execute a query
        when it is called!
        """
        query, arguments = self._prepare_query_and_arguments(
            sql_statement, parameters
        )
        rows = self._execute_sql_statement(query, arguments)
        return (model(*row) for row in rows) if model else rows

    def execute_many(
            self, sql_statement: Union[str, StringDump],
            parameters: Iterable[Iterable] = (()), model: MaybeModel = None
    ) -> Iterable[Iterable[Union[Sequence, GenericModel]]]:
        """
        Like .execute(), but executes the same query multiple times with
        different arguments
        """
        results = []
        for parameters_list in parameters:
            results.append(self.execute(sql_statement, parameters_list, model))
        return results

    @abstractmethod
    def _execute_sql_statement(
            self, statement: str, parameters: list) -> Iterable[Sequence]:
        """
        This thingy should return an iterable of rows (or just a stub-iterable,
        like an empty tuple, if there is nothing to return)
        """
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def create_tables(self, *tables: Type[ModelBase]):
        pass


class EmptyAsyncIterator:

    def __anext__(self):
        raise StopAsyncIteration


class EmptyAsyncIterable:

    def __aenter__(self):
        return EmptyAsyncIterator()


class AbstractAsyncSQLExecutor(AbstractSQLExecutor, ABC):

    async def execute(
        self, sql_statement: Union[str, StringDump],
        parameters: Iterable = (), model: MaybeModel = None
    ) -> AsyncIterable[Union[Sequence, GenericModel]]:
        query, arguments = self._prepare_query_and_arguments(
            sql_statement, parameters
        )
        rows = await self._execute_sql_statement(query, arguments)
        return (model(*row) async for row in rows) if model else rows

    @abstractmethod
    async def _execute_sql_statement(
            self, statement: str, parameters: list) -> AsyncIterable[Sequence]:
        """
        This thingy should return an asynchronous iterable of rows (or just a
        stub-iterable, like an EmptyAsyncIterable from this module, if there is
        nothing to return)
        """
        pass

    async def execute_many(
        self, sql_statement: Union[str, StringDump],
        parameters: Iterable[Iterable] = (()), model: MaybeModel = None
    ) -> Iterable[Iterable[Union[Sequence, GenericModel]]]:
        """
        Like .execute(), but executes the same query multiple times with
        different arguments
        """
        for parameters_list in parameters:
            yield await self.execute(sql_statement, parameters_list, model)

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def create_tables(self, *tables: Type[ModelBase]):
        pass
