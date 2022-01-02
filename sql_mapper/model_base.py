from typing import Dict, Any, Iterable


class ModelBase:
    _fields: Dict[str, str]
    _tablename: str = ""
    _additional_table_lines: str = ""

    def __init_subclass__(cls, **kwargs):
        cls._fields = {}
        excluded_fields = {
            field
            for field in vars(cls)
            if field.startswith("_")
        }
        for field_name, field_value in vars(cls).items():
            if (
                not callable(field_value)
                and field_name not in excluded_fields
            ):
                cls._fields[field_name] = field_value
        return cls

    def __new__(cls, *ordered_fields, **keyword_fields):
        instance = super().__new__(cls)
        fields = {}
        for field_name, field_value in zip(cls._fields.keys(), ordered_fields):
            fields[field_name] = field_value
        for key, value in keyword_fields.items():
            if key not in cls._fields:
                raise ValueError(f"Invalid field name: {keyword_fields}")
            fields[key] = value
        for field_name in cls._fields:
            if field_name not in fields:
                raise ValueError(f"Field wasn't initialized: {field_name}")
        for field_name, field_value in fields.items():
            setattr(instance, field_name, field_value)
        instance._fields = fields
        return instance

    def __eq__(self, other: "ModelBase"):
        return all(
            left == right
            for left, right in zip(self.values(), other.values())
        )

    def values(self) -> Iterable[Any]:
        return self._fields.values()

    @classmethod
    def fields_amount(cls):
        return len(cls._fields)

    @classmethod
    def get_table_creation_sql(cls):
        if not cls._tablename:
            raise ValueError("You need to specify a _tablename!")
        sql_statement = (
            f"CREATE TABLE IF NOT EXISTS {cls._tablename} ("
            + ",".join(
                f"{field_name} {field_value}"
                for field_name, field_value in cls._fields.items()
            )
            + (
                f",{cls._additional_table_lines}"
                if cls._additional_table_lines else
                ""
            ) + ")"
        )
        return sql_statement

    def __str__(self):
        arguments = ", ".join(
            f"{field_name}={repr(field_value)}"
            for field_name, field_value in self._fields.items()
        )
        return f"{self.__class__.__name__}({arguments})"
