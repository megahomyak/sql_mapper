from dataclasses import dataclass
from typing import Dict, Any, Union, Optional

from sql_mapper import exceptions


@dataclass
class TableData:
    name: Optional[str]
    fields: Dict[str, str]
    additional_table_lines: Optional[str]


class ModelBase:
    _fields: Dict[str, Union[str, Any]]
    _tablename: str
    _additional_table_lines: str

    @staticmethod
    def _field_is_valid(field_name: str, field_value: Any):
        return not (callable(field_value) or field_name.startswith("_"))

    def __init_subclass__(cls, **kwargs):
        cls._fields = {}
        fields = {
            field_name: None
            for field_name in cls.__annotations__
            if cls._field_is_valid(field_name, None)
        }
        fields.update({
            field_name: field_value
            for field_name, field_value in vars(cls).items()
            if cls._field_is_valid(field_name, field_value)
        })
        cls._fields = fields
        return cls

    def __init__(self, *ordered_fields, **keyword_fields):
        _fields = keyword_fields
        class_fields = self.__class__._fields
        for field_name in _fields:
            if field_name not in class_fields:
                raise exceptions.UnknownField(field_name)
        if len(class_fields) < len(ordered_fields):
            raise exceptions.TooManyOrderedFields(
                model_name=self.__class__.__name__,
                given_amount=len(ordered_fields),
                actual_amount=len(class_fields)
            )
        for field_name, field_value in zip(class_fields, ordered_fields):
            if field_name in _fields:
                raise exceptions.FieldAlreadyTaken(field_name)
            _fields[field_name] = field_value
        self._fields = _fields

    def __getattr__(self, field_name: str):
        return self.instance_fields[field_name]

    def __eq__(self, other: "ModelBase"):
        return self.instance_fields == other.instance_fields

    @classmethod
    def get_tablename(cls) -> Optional[str]:
        try:
            return cls._tablename
        except AttributeError:
            return None

    @property
    def instance_fields(self) -> Dict[str, str]:
        return self._fields

    @classmethod
    def get_table_data(cls):
        name = cls.get_tablename()
        fields = cls._fields
        try:
            additional_table_lines = cls._additional_table_lines
        except AttributeError:
            additional_table_lines = None
        return TableData(name, fields, additional_table_lines)

    def __str__(self):
        arguments = ", ".join(
            f"{field_name}={repr(field_value)}"
            for field_name, field_value in self.instance_fields.items()
        )
        return f"{self.__class__.__name__}({arguments})"

    def __repr__(self):
        return f"<{str(self)} at {hex(id(self))}>"
