import re
import typing
from abc import ABC, abstractmethod
from typing import Union, List, Iterable

from sql_mapper import exceptions
from sql_mapper.model_base import ModelBase

QUESTION_MARK_PATTERN = re.compile(r"\?")


class BaseFormattableString(ABC):

    def __init__(self, query: str):
        self.query = query

    def __str__(self):
        return f"{self.__class__.__name__}({repr(self.query)})"

    def __eq__(self, other: "BaseFormattableString"):
        return type(other) == type(self) and other.query == self.query

    @abstractmethod
    def reformat_query(
            self, old_arguments: Iterable, new_arguments: list,
            new_parameter_mark: str,
            old_parameter_mark: re.Pattern = QUESTION_MARK_PATTERN
    ) -> str:
        """
        Makes a query that can be passed to the database connector, replacing
        every BaseModel instance with its values and its corresponding
        question mark with something like "tablename (field1, field2, field3)
        VALUES (?,?,?)" (depends on the database connector).

        So,

        old query:
            "INSERT INTO ?", instance_of_model
        new query:
            "INSERT INTO tablename (field1, field2, ...) VALUES (?, ?, ...)",
            values_from_instance_of_model
        """
        pass


class FormattableString(BaseFormattableString):

    @staticmethod
    def _new_query_parameter_marks_generator(
            old_arguments: Iterable, new_arguments: list,
            new_parameter_mark: str):
        """
        Yields new parameter marks, which will replace old parameter marks.
        Also appends additional new arguments to new_arguments (passed list).
        """
        for argument in old_arguments:
            if isinstance(argument, ModelBase):
                new_arguments.extend(argument.instance_fields.values())
                tablename = argument.get_tablename()
                if not tablename:
                    raise exceptions.TablenameNotSpecifiedOnInsertion(
                        model_name=argument.__class__.__name__
                    )
                yield (
                    tablename + "(" + ",".join(argument.instance_fields.keys())
                    + ")VALUES(" + ",".join(
                        new_parameter_mark
                        for _ in range(len(argument.instance_fields))
                    ) + ")"
                )
            else:
                new_arguments.append(argument)
                yield new_parameter_mark

    def reformat_query(
            self, old_arguments: Iterable, new_arguments: list,
            new_parameter_mark: str,
            old_parameter_mark: re.Pattern = QUESTION_MARK_PATTERN
    ):
        parameter_marks_generator = self._new_query_parameter_marks_generator(
            old_arguments, new_arguments, new_parameter_mark
        )
        new_query = old_parameter_mark.sub(
            lambda match: next(parameter_marks_generator), self.query
        )
        return new_query


class UnformattableString(BaseFormattableString):

    def reformat_query(
            self, old_arguments: Iterable, new_arguments: list,
            new_parameter_mark: str,
            old_parameter_mark: re.Pattern = QUESTION_MARK_PATTERN
    ) -> str:
        return self.query


class NewQueryStringWithArguments(typing.NamedTuple):
    query: str
    arguments: list


class StringDump:

    def __init__(self):
        self.strings: List[BaseFormattableString] = []

    def __add__(self, other_query_part: Union[str, "StringDump"]):
        if isinstance(other_query_part, str):
            self.strings.append(FormattableString(other_query_part))
        else:
            self.strings.extend(other_query_part.strings)
        return self

    def __radd__(self, other_query_part: Union[str, "StringDump"]):
        if isinstance(other_query_part, str):
            self.strings.insert(0, FormattableString(other_query_part))
        else:
            for index in range(len(other_query_part.strings)):
                self.strings.insert(
                    index, other_query_part.strings[index]
                )
        return self

    def reformat_collected_query(
            self, old_arguments: Iterable, new_parameter_mark: str,
            old_parameter_mark: re.Pattern = QUESTION_MARK_PATTERN
    ) -> NewQueryStringWithArguments:
        """
        old query:
            INSERT INTO ?
        old arguments:
            instance_of_model
        new query:
            INSERT INTO tablename (field1, field2, ...) VALUES (?, ?, ...)
        new arguments:
            values_from_instance_of_model
        """
        new_arguments = []
        new_query = "".join(
            string.reformat_query(
                old_arguments, new_arguments, new_parameter_mark,
                old_parameter_mark
            )
            for string in self.strings
        )
        return NewQueryStringWithArguments(new_query, new_arguments)

    def __str__(self):
        return "[" + ", ".join(str(string) for string in self.strings) + "]"


def raw(query_part: str):
    string_dump = StringDump()
    string_dump.strings.append(UnformattableString(query_part))
    return string_dump
