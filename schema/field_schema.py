from typing import TYPE_CHECKING

from app.category import Category
from schema.field_type import FieldType

if TYPE_CHECKING:
    from schema.data_schema import DataSchema


class FieldSchema:

    def __init__(self, data_schema: 'DataSchema', name: str):
        self.data_schema: 'DataSchema' = data_schema
        self.original_name: str = name
        self.readable_name: str = name
        self.synonyms: dict[str, list[str]] = {'en': []}
        self.type: FieldType = FieldType('string')
        self.num_different_values: int = self.data_schema.data_source.df[self.original_name].nunique()
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

    def _update_categories(self):
        if self._categorical and self.categories is None:
            self.categories = []
            for category in self.data_schema.data_source.df[self.original_name].unique():
                self.categories.append(Category(category))

    def get_category(self, value: str):
        if self._categorical and self.categories:
            for category in self.categories:
                if category.value == value:
                    return category
        return None

