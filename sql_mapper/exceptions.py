class TooManyOrderedFields(Exception):

    def __init__(self, model_name: str, given_amount: int, actual_amount: int):
        self.given_amount = given_amount
        self.actual_amount = actual_amount
        self.model_name = model_name

    def __str__(self):
        return (
            f"model '{self.model_name}' has {self.actual_amount} fields, but "
            f"{self.given_amount} ordered fields was given"
        )


class _FieldNameMixin:

    def __init__(self, field_name: str):
        self.field_name = field_name


class FieldAlreadyTaken(_FieldNameMixin, Exception):

    def __str__(self):
        return (
            f"field '{self.field_name}' was already filled! Check your ordered "
            f"fields, it may help"
        )


class UnknownField(_FieldNameMixin, Exception):

    def __str__(self):
        return (
            f"unknown field '{self.field_name}'! (It is not declared in the "
            f"model)"
        )


class _ModelNameMixin:

    def __init__(self, model_name: str):
        self.model_name = model_name


class TablenameNotSpecifiedOnTableCreation(_ModelNameMixin, Exception):

    def __str__(self):
        return (
            f"tablename not specified for the model '{self.model_name}'! You "
            f"cannot create an unnamed table!"
        )


class TablenameNotSpecifiedOnInsertion(_ModelNameMixin, Exception):

    def __str__(self):
        return (
            f"tablename not specified for the model '{self.model_name}'! SQL "
            f"mapper doesn't know what tablename to use in query parameter "
            f"mark substitution, so add the tablename to the model!"
        )
