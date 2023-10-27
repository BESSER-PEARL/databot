from typing import TYPE_CHECKING

from pandas import DataFrame

from schema.data_schema import DataSchema

if TYPE_CHECKING:
    from app.project import Project


class DataSource:

    def __init__(self, project: 'Project', name: str, df: DataFrame):
        self.project: 'Project' = project
        self.name: str = name
        self.df: DataFrame = df
        self.data_schema: DataSchema = DataSchema(self)

        self.project.add_data_source(self)

    def get_field(self, name: str):
        return self.data_schema.get_field(name)
