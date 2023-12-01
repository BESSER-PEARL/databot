import json
from typing import TYPE_CHECKING

from besser.bot.core.intent.intent import Intent
from besser.bot.library.entity.base_entities import any_entity, datetime_entity, number_entity

from app.bot.library import session_keys

if TYPE_CHECKING:
    from app.bot.databot import DataBot


def load_intent(name: str, name_json: str or None = None):
    """Load an intent and its training sentences from a json file"""
    with open('app/bot/library/intents.json', 'r', encoding='utf-8') as file:
        intents_json = json.load(file)
    if name_json is None:
        name_json = name
    training_sentences = intents_json[name_json]
    return Intent(name, training_sentences)


class DataBotIntents:
    """All the intents used by the DataBot"""

    def __init__(self, databot: 'DataBot'):
        self.histogram_chart = databot.bot.add_intent(load_intent('histogram_chart'))
        self.histogram_chart.parameter(session_keys.FIELD, 'FIELD', databot.entities.field)

        self.line_chart = databot.bot.add_intent(load_intent('line_chart'))
        self.line_chart.parameter(session_keys.FIELD_X, 'FIELD_X', databot.entities.field)
        self.line_chart.parameter(session_keys.FIELD_Y, 'FIELD_Y', databot.entities.field)

        self.bar_chart = databot.bot.add_intent(load_intent('bar_chart'))
        self.bar_chart.parameter(session_keys.FIELD_X, 'FIELD_X', databot.entities.field)
        self.bar_chart.parameter(session_keys.FIELD_Y, 'FIELD_Y', databot.entities.field)


        self.reset = databot.bot.add_intent(load_intent('reset'))

        self.show_data = databot.bot.add_intent(load_intent('show_data'))

        self.show_all = databot.bot.add_intent(load_intent('show_all'))

        self.show_all_distinct = databot.bot.add_intent(load_intent('show_all_distinct'))

        self.show_next_page = databot.bot.add_intent(load_intent('show_next_page'))

        self.show_previous_page = databot.bot.add_intent(load_intent('show_previous_page'))

        self.add_filter = databot.bot.add_intent(load_intent('add_filter'))

        self.remove_filter = databot.bot.add_intent(load_intent('remove_filter'))

        self.add_field_to_view = databot.bot.add_intent(load_intent('add_field_to_view'))

        self.structured_query = databot.bot.add_intent(load_intent('structured_query'))

        self.custom_query = databot.bot.add_intent(load_intent('custom_query'))

        self.another_query = databot.bot.add_intent(load_intent('another_query'))

        self.i_dont_know = databot.bot.add_intent(load_intent('i_dont_know'))

        self.numeric_field = databot.bot.add_intent(load_intent('numeric_field', 'value'))
        self.numeric_field.parameter(session_keys.VALUE, 'VALUE', databot.entities.numeric_field)

        self.textual_field = databot.bot.add_intent(load_intent('textual_field', 'value'))
        self.textual_field.parameter(session_keys.VALUE, 'VALUE', databot.entities.textual_field)

        self.datetime_field = databot.bot.add_intent(load_intent('datetime_field', 'value'))
        self.datetime_field.parameter(session_keys.VALUE, 'VALUE', databot.entities.datetime_field)

        self.field = databot.bot.add_intent(load_intent('field', 'value'))
        self.field.parameter(session_keys.VALUE, 'VALUE', databot.entities.field)

        self.numeric_operator = databot.bot.add_intent(load_intent('numeric_operator', 'value'))
        self.numeric_operator.parameter(session_keys.VALUE, 'VALUE', databot.entities.numeric_operator)

        self.textual_operator = databot.bot.add_intent(load_intent('textual_operator', 'value'))
        self.textual_operator.parameter(session_keys.VALUE, 'VALUE', databot.entities.textual_operator)

        self.datetime_operator = databot.bot.add_intent(load_intent('datetime_operator', 'value'))
        self.datetime_operator.parameter(session_keys.VALUE, 'VALUE', databot.entities.datetime_operator)

        self.numeric_function_operator = databot.bot.add_intent(load_intent('numeric_function_operator', 'value'))
        self.numeric_function_operator.parameter(session_keys.VALUE, 'VALUE', databot.entities.numeric_function_operator)

        self.datetime_function_operator = databot.bot.add_intent(load_intent('datetime_function_operator', 'value'))
        self.datetime_function_operator.parameter(session_keys.VALUE, 'VALUE', databot.entities.datetime_function_operator)

        self.show_field_distinct = databot.bot.add_intent(load_intent('show_field_distinct'))
        self.show_field_distinct.parameter(session_keys.FIELD, 'FIELD', databot.entities.field)

        self.most_frequent_value_in_field = databot.bot.add_intent(load_intent('most_frequent_value_in_field'))
        self.most_frequent_value_in_field.parameter(session_keys.FIELD, 'FIELD', databot.entities.field)
        self.most_frequent_value_in_field.parameter(session_keys.ROW_NAME, 'ROW_NAME', databot.entities.row_name)

        self.least_frequent_value_in_field = databot.bot.add_intent(load_intent('least_frequent_value_in_field'))
        self.least_frequent_value_in_field.parameter(session_keys.FIELD, 'FIELD', databot.entities.field)
        self.least_frequent_value_in_field.parameter(session_keys.ROW_NAME, 'ROW_NAME', databot.entities.row_name)

        self.value_frequency = databot.bot.add_intent(load_intent('value_frequency'))
        self.value_frequency.parameter(session_keys.VALUE, 'VALUE', databot.entities.field_value)

        self.value1_more_than_value2 = databot.bot.add_intent(load_intent('value1_more_than_value2'))
        self.value1_more_than_value2.parameter(session_keys.VALUE + '1', 'VALUE', databot.entities.field_value)
        self.value1_more_than_value2.parameter(session_keys.VALUE + '2', 'VALUE', databot.entities.field)

        self.value1_less_than_value2 = databot.bot.add_intent(load_intent('value1_less_than_value2'))
        self.value1_less_than_value2.parameter(session_keys.VALUE + '1', 'VALUE', databot.entities.field_value)
        self.value1_less_than_value2.parameter(session_keys.VALUE + '2', 'VALUE', databot.entities.field)

        self.row_count = databot.bot.add_intent(load_intent('row_count'))
        self.row_count.parameter(session_keys.ROW_NAME, 'ROW_NAME', databot.entities.row_name)

        self.field_count = databot.bot.add_intent(load_intent('field_count'))
        self.field_count.parameter(session_keys.ROW_NAME, 'ROW_NAME', databot.entities.row_name)

        self.select_fields_with_conditions = databot.bot.add_intent(load_intent('select_fields_with_conditions'))
        self.select_fields_with_conditions.parameter(session_keys.NUMBER, 'NUMBER', number_entity)
        self.select_fields_with_conditions.parameter(session_keys.FIELD + '1', 'FIELD1', databot.entities.field)
        self.select_fields_with_conditions.parameter(session_keys.ROW_NAME, 'ROW_NAME', databot.entities.row_name)
        self.select_fields_with_conditions.parameter(session_keys.OPERATOR, 'OPERATOR', databot.entities.function_operator)
        self.select_fields_with_conditions.parameter(session_keys.FIELD + '2', 'FIELD2', databot.entities.field)
        self.select_fields_with_conditions.parameter(session_keys.VALUE + '1', 'VALUE1', databot.entities.field_value)
        self.select_fields_with_conditions.parameter(session_keys.VALUE + '2', 'VALUE2', databot.entities.field_value)

        self.numeric_field_operator_value = databot.bot.add_intent(load_intent('numeric_field_operator_value', 'field_operator_value'))
        self.numeric_field_operator_value.parameter(session_keys.ROW_NAME, 'ROW_NAME', databot.entities.row_name)
        self.numeric_field_operator_value.parameter(session_keys.FIELD, 'FIELD', databot.entities.numeric_field)
        self.numeric_field_operator_value.parameter(session_keys.OPERATOR, 'OPERATOR', databot.entities.numeric_operator)
        self.numeric_field_operator_value.parameter(session_keys.VALUE, 'VALUE', number_entity)

        self.datetime_field_operator_value = databot.bot.add_intent(load_intent('datetime_field_operator_value', 'field_operator_value'))
        self.datetime_field_operator_value.parameter(session_keys.ROW_NAME, 'ROW_NAME', databot.entities.row_name)
        self.datetime_field_operator_value.parameter(session_keys.FIELD, 'FIELD', databot.entities.datetime_field)
        self.datetime_field_operator_value.parameter(session_keys.OPERATOR, 'OPERATOR', databot.entities.datetime_operator)
        self.datetime_field_operator_value.parameter(session_keys.VALUE, 'VALUE', datetime_entity)

        self.textual_field_operator_value = databot.bot.add_intent(load_intent('textual_field_operator_value', 'field_operator_value'))
        self.textual_field_operator_value.parameter(session_keys.ROW_NAME, 'ROW_NAME', databot.entities.row_name)
        self.textual_field_operator_value.parameter(session_keys.FIELD, 'FIELD', databot.entities.textual_field)
        self.textual_field_operator_value.parameter(session_keys.OPERATOR, 'OPERATOR', databot.entities.textual_operator)
        self.textual_field_operator_value.parameter(session_keys.VALUE, 'VALUE', any_entity)
        # TODO: any not implemented

        self.numeric_field_between_values = databot.bot.add_intent(load_intent('numeric_field_between_values', 'field_between_values'))
        self.numeric_field_between_values.parameter(session_keys.ROW_NAME, 'ROW_NAME', databot.entities.row_name)
        self.numeric_field_between_values.parameter(session_keys.FIELD, 'FIELD', databot.entities.row_name)
        self.numeric_field_between_values.parameter(session_keys.VALUE + '1', 'VALUE1', databot.entities.row_name)
        self.numeric_field_between_values.parameter(session_keys.VALUE + '2', 'VALUE2', databot.entities.row_name)

        self.datetime_field_between_values = databot.bot.add_intent(load_intent('datetime_field_between_values', 'field_between_values'))
        self.datetime_field_between_values.parameter(session_keys.ROW_NAME, 'ROW_NAME', databot.entities.row_name)
        self.datetime_field_between_values.parameter(session_keys.FIELD, 'FIELD', databot.entities.row_name)
        self.datetime_field_between_values.parameter(session_keys.VALUE + '1', 'VALUE1', databot.entities.row_name)
        self.datetime_field_between_values.parameter(session_keys.VALUE + '2', 'VALUE2', databot.entities.row_name)
