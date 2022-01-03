from dataclasses import dataclass
from typing import Dict, Any, Union


@dataclass
class TableData:
    name: str
    fields: Dict[str, str]
    additional_table_lines: str


class ModelBase:
    _fields: Dict[str, Union[str, Any]]
    _tablename: str = ""
    _additional_table_lines: str = ""

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
        for field_name, field_value in zip(self._fields, ordered_fields):
            _fields[field_name] = field_value
        self._fields = _fields

    def __getattr__(self, field_name: str):
        return self.instance_fields[field_name]

    def __eq__(self, other: "ModelBase"):
        return self.instance_fields == other.instance_fields

    @property
    def instance_fields(self) -> Dict[str, str]:
        return self._fields

    @classmethod
    def get_table_data(cls):
        if not cls._tablename:
            raise ValueError(
                "You need to specify a _tablename to get table data!"
            )
        return TableData(
            name=cls._tablename, fields=cls._fields,
            additional_table_lines=cls._additional_table_lines
        )

    def __str__(self):
        arguments = ", ".join(
            f"{field_name}={repr(field_value)}"
            for field_name, field_value in self.instance_fields.items()
        )
        return f"{self.__class__.__name__}({arguments})"

    def __repr__(self):
        return f"<{str(self)} at {hex(id(self))}>"
