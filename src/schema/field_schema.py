from typing import TYPE_CHECKING

import pandas as pd

from src.schema.category import Category
from src.schema.field_type import BOOLEAN, DATETIME, FieldType, NUMERIC, TEXTUAL

if TYPE_CHECKING:
    from src.schema.data_schema import DataSchema


class FieldSchema:

    def __init__(self, data_schema: 'DataSchema', name: str):
        self.data_schema: 'DataSchema' = data_schema
        self.original_name: str = name
        self.readable_name: str = name
        self.synonyms: dict[str, list[str]] = {'en': []}
        t = self.data_schema.project.df[self.original_name].dtype
        if t == 'int64' or t == 'float64':
            t = NUMERIC
        elif t == 'bool':
            # TODO: YES/NO, 0/1 columns, boolean?
            t = BOOLEAN
        elif t in ['datetime64[ns]', '<M8[ns]']:
            t = DATETIME
        elif t == 'object':
            # Check if it is datetime
            if self.infer_datetime_type(self.original_name):
                t = DATETIME
            else:
                t = TEXTUAL
        self.type: FieldType = FieldType(t)  # TODO: infer type (datetime, etc)
        self.num_different_values: int = self.data_schema.project.df[self.original_name].nunique()
        self.key: bool = False
        self._categorical: bool = self.num_different_values < 10
        self.categories: list[Category] or None = None
        self._update_categories()

        self.tags: list[str] = []

    @property
    def categorical(self):
        return self._categorical

    @categorical.setter
    def categorical(self, value):
        self._categorical = value
        self._update_categories()

    def get_category(self, value: str) -> Category:
        for category in self.categories:
            if category.value == value:
                return category
        return None

    def _update_categories(self):
        if self._categorical and self.categories is None:
            self.categories = []
            for category in self.data_schema.project.df[self.original_name].unique():
                self.categories.append(Category(category))

    def get_category(self, value: str):
        if self._categorical and self.categories:
            for category in self.categories:
                if category.value == value:
                    return category
        return None

    def to_dict(self):
        field_schema_dict = {
            # 'original_name': self.original_name,
            'readable_name': self.readable_name,
            'type': self.type.t,
            'num_different_values': self.num_different_values,
            'synonyms': self.synonyms['en']
            # 'key': self.key,
            # 'categorical': self.categorical,
            # 'tags': self.tags,
        }
        if self.categorical:
            field_schema_dict['categories'] = {category.value: category.to_dict() for category in self.categories}
        return field_schema_dict

    def to_dict_simple(self):
        field_schema_dict = {
            'type': self.type.t,
        }
        if self.categorical:
            field_schema_dict['categories'] = {category.value: category.to_dict_simple() for category in self.categories}
        if self.synonyms['en']:
            field_schema_dict['synonyms'] = self.synonyms['en']
        return field_schema_dict

    def infer_datetime_type(self, column_name):
        df = self.data_schema.project.df
        # TODO: datetime formats
        date_formats = [
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%d/%m',
        ]
        for date_format in date_formats:
            try:
                df[column_name] = pd.to_datetime(df[column_name], format=date_format)
                return True
            except ValueError as e:
                pass
        return False
