from typing import Any

from schema.field_schema import FieldSchema


class Filter:

    def __init__(self, field: FieldSchema, operator: str, value: Any):
        self.field: FieldSchema = field
        self.operator: str = operator
        self.value: Any = value

    def __eq__(self, other):
        if type(other) is type(self):
            return self.field == other.field and self.operator == other.operator and self.value == other.value
        else:
            return False
