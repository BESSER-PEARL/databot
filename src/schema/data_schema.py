from typing import TYPE_CHECKING

from src.schema.field_schema import FieldSchema

if TYPE_CHECKING:
    from src.app.project import Project


class DataSchema:

    def __init__(self, project: 'Project'):
        self.project: 'Project' = project
        self.field_schemas: list[FieldSchema] = []
        # TODO: Add row names
        for column in self.project.df.columns:
            self.field_schemas.append(FieldSchema(self, column))

    def get_field(self, name: str):
        for field in self.field_schemas:
            if field.original_name == name:
                return field
        return None

    def to_dict(self):
        return {field_schema.original_name: field_schema.to_dict() for field_schema in self.field_schemas}

    def to_dict_simple(self):
        return {field_schema.original_name: field_schema.to_dict_simple() for field_schema in self.field_schemas}

    def get_key_fields(self) -> list[FieldSchema]:
        key_fields: list[FieldSchema] = []
        for field in self.field_schemas:
            if field.key:
                key_fields.append(field)
        return key_fields
