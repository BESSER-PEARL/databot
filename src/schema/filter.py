import logging
from typing import Any

import numpy as np
from pandas import DataFrame

from src.schema.field_schema import FieldSchema
from src.schema.field_type import BOOLEAN, DATETIME, NUMERIC, TEXTUAL

numeric_operators = ['=', '!=', '<', '<=', '>', '>=']
textual_operators = ['equals', 'different', 'contains', 'starts with', 'ends with']
datetime_operators = ['equals', 'different', 'between', 'before', 'after']
boolean_operators = ['equals']


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

    def apply(self, df):
        if self.field.type.t == NUMERIC:
            return self.apply_numeric_filter(df)
        if self.field.type.t == TEXTUAL:
            return self.apply_textual_filter(df)
        if self.field.type.t == DATETIME:
            return self.apply_datetime_filter(df)
        if self.field.type.t == BOOLEAN:
            return self.apply_boolean_filter(df)

    def apply_numeric_filter(self, df: DataFrame):
        if self.operator == '=':
            return df[df[self.field.original_name] == self.value]
        elif self.operator == '!=':
            return df[df[self.field.original_name] != self.value]
        elif self.operator == '<':
            return df[df[self.field.original_name] < self.value]
        elif self.operator == '<=':
            return df[df[self.field.original_name] <= self.value]
        elif self.operator == '>':
            return df[df[self.field.original_name] > self.value]
        elif self.operator == '>=':
            return df[df[self.field.original_name] >= self.value]
        logging.warning('No numeric filter could be applied')
        return df

    def apply_textual_filter(self, df: DataFrame):
        if self.operator == 'equals':
            return df[df[self.field.original_name] == self.value]
        if self.operator == 'different':
            return df[df[self.field.original_name] != self.value]
        if self.operator == 'contains':
            return df[df[self.field.original_name].str.contains(self.value)]
        if self.operator == 'starts with':
            return df[df[self.field.original_name].str.startswith(self.value)]
        if self.operator == 'ends with':
            return df[df[self.field.original_name].str.endswith(self.value)]
        logging.warning('No textual filter could be applied')
        return df

    def apply_datetime_filter(self, df: DataFrame):
        # datetime value: [(date, time)]
        # date or time can be None
        # if operator is 'between': [(date1, time1), (date2, time2)]
        # date1 and date2, or time1 and time2, can be null
        # TODO: Use the time field for the datetime filter
        if self.operator == 'equals':
            return df[df[self.field.original_name] == np.datetime64(self.value[0][0])]
        if self.operator == 'different':
            return df[df[self.field.original_name] != np.datetime64(self.value[0][0])]
        if self.operator == 'between':
            return df[(np.datetime64(self.value[0][0]) <= df[self.field.original_name]) & (df[self.field.original_name] <= np.datetime64(self.value[1][0]))]
        if self.operator == 'before':
            return df[df[self.field.original_name] < np.datetime64(self.value[0][0])]
        if self.operator == 'after':
            return df[df[self.field.original_name] > np.datetime64(self.value[0][0])]
        logging.warning('No datetime filter could be applied')
        return df

    def apply_boolean_filter(self, df: DataFrame):
        if self.operator == 'equals':
            return df[df[self.field.original_name] == self.value]
        logging.warning('No textual filter could be applied')
        return df
