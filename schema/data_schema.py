from typing import TYPE_CHECKING

from schema.field_schema import FieldSchema

if TYPE_CHECKING:
    from app.data_source import DataSource


class DataSchema:

    def __init__(self, data_source: 'DataSource'):
        self.data_source: 'DataSource' = data_source
        self.field_schemas: list[FieldSchema] = []
        for column in self.data_source.df.columns:
            self.field_schemas.append(FieldSchema(self, column))

    def get_field(self, name: str):
        for field in self.field_schemas:
            if field.original_name == name:
                return field
        return None

    def to_dict(self):
        return {'field_schemas': [field_schema.to_dict() for field_schema in self.field_schemas]}
