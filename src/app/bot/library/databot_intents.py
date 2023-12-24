import json
from typing import TYPE_CHECKING

from besser.bot.core.intent.intent import Intent
from besser.bot.library.entity.base_entities import number_entity

from src.app.bot.library import session_keys

if TYPE_CHECKING:
    from src.app.bot.databot import DataBot


def load_intent(name: str, name_json: str or None = None):
    """Load an intent and its training sentences from a json file"""
    with open('src/app/bot/library/intents.json', 'r', encoding='utf-8') as file:
        intents_json = json.load(file)
    if name_json is None:
        name_json = name
    training_sentences = intents_json[name_json]
    return Intent(name, training_sentences)


class DataBotIntents:
    """All the intents used by the DataBot"""

    def __init__(self, databot: 'DataBot'):

        # Plots/Charts

        self.histogram_chart = databot.bot.add_intent(load_intent('histogram_chart'))
        self.histogram_chart.parameter(session_keys.FIELD, 'FIELD', databot.entities.field)

        self.line_chart = databot.bot.add_intent(load_intent('line_chart'))
        self.line_chart.parameter(session_keys.FIELD_X, 'FIELD_X', databot.entities.field)
        self.line_chart.parameter(session_keys.FIELD_Y, 'FIELD_Y', databot.entities.field)

        self.bar_chart = databot.bot.add_intent(load_intent('bar_chart'))
        self.bar_chart.parameter(session_keys.FIELD_Y, 'FIELD_Y', databot.entities.field)
        self.bar_chart.parameter(session_keys.FIELD_X, 'FIELD_X', databot.entities.field)

        self.pie_chart = databot.bot.add_intent(load_intent('pie_chart'))
        self.pie_chart.parameter(session_keys.FIELD_X, 'FIELD_X', databot.entities.field)  # TODO: Only numeric fields
        self.pie_chart.parameter(session_keys.FIELD_Y, 'FIELD_Y', databot.entities.field)

        self.scatter_chart = databot.bot.add_intent(load_intent('scatter_chart'))
        self.scatter_chart.parameter(session_keys.FIELD_X, 'FIELD_X', databot.entities.numeric_field)
        self.scatter_chart.parameter(session_keys.FIELD_Y, 'FIELD_Y', databot.entities.numeric_field)

        self.area_chart = databot.bot.add_intent(load_intent('area_chart'))
        self.area_chart.parameter(session_keys.FIELD_X, 'FIELD_X', databot.entities.field)
        self.area_chart.parameter(session_keys.FIELD_Y, 'FIELD_Y', databot.entities.field)

        self.boxplot_chart = databot.bot.add_intent(load_intent('boxplot_chart'))
        self.boxplot_chart.parameter(session_keys.FIELD, 'FIELD', databot.entities.numeric_field)

        # Tables

        self.field_distinct = databot.bot.add_intent(load_intent('field_distinct'))
        self.field_distinct.parameter(session_keys.FIELD, 'FIELD', databot.entities.field)

        self.most_frequent_value_in_field = databot.bot.add_intent(load_intent('most_frequent_value_in_field'))
        self.most_frequent_value_in_field.parameter(session_keys.FIELD, 'FIELD', databot.entities.field)
        self.most_frequent_value_in_field.parameter(session_keys.ROW_NAME, 'ROW_NAME', databot.entities.row_name)

        self.least_frequent_value_in_field = databot.bot.add_intent(load_intent('least_frequent_value_in_field'))
        self.least_frequent_value_in_field.parameter(session_keys.FIELD, 'FIELD', databot.entities.field)
        self.least_frequent_value_in_field.parameter(session_keys.ROW_NAME, 'ROW_NAME', databot.entities.row_name)

        self.value_frequency = databot.bot.add_intent(load_intent('value_frequency'))
        self.value_frequency.parameter(session_keys.VALUE, 'VALUE', databot.entities.field_value)

        self.value1_vs_value2 = databot.bot.add_intent(load_intent('value1_vs_value2'))
        self.value1_vs_value2.parameter(session_keys.VALUE + '1', 'VALUE1', databot.entities.field_value)
        self.value1_vs_value2.parameter(session_keys.VALUE + '2', 'VALUE2', databot.entities.field_value)

        self.select_fields_with_conditions = databot.bot.add_intent(load_intent('select_fields_with_conditions'))
        self.select_fields_with_conditions.parameter(session_keys.NUMBER, 'NUMBER', number_entity)
        self.select_fields_with_conditions.parameter(session_keys.FIELD + '1', 'FIELD1', databot.entities.field)
        self.select_fields_with_conditions.parameter(session_keys.ROW_NAME, 'ROW_NAME', databot.entities.row_name)
        self.select_fields_with_conditions.parameter(session_keys.OPERATOR, 'OPERATOR', databot.entities.function_operator)
        self.select_fields_with_conditions.parameter(session_keys.FIELD + '2', 'FIELD2', databot.entities.field)
        self.select_fields_with_conditions.parameter(session_keys.VALUE + '1', 'VALUE1', databot.entities.field_value)
        self.select_fields_with_conditions.parameter(session_keys.VALUE + '2', 'VALUE2', databot.entities.field_value)
