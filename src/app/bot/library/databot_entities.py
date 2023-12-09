import json
from typing import TYPE_CHECKING

from besser.bot.core.entity.entity import Entity

from src.schema.field_type import DATETIME, NUMERIC, TEXTUAL

if TYPE_CHECKING:
    from src.app.bot.databot import DataBot


def generate_field_entity(databot: 'DataBot', t: str or None = None) -> Entity:
    entries = {}
    for field_schema in databot.project.data_schema.field_schemas:
        if not t or field_schema.type.t == t:
            entries[field_schema.original_name] = field_schema.synonyms['en'].copy()
            if field_schema.readable_name and field_schema.readable_name != field_schema.original_name:
                entries[field_schema.original_name] += [field_schema.readable_name]
    if not t:
        name = 'field'
    else:
        name = t + '_field'
    return Entity(name, entries=entries)


def generate_operator_entity(name: str) -> Entity:
    entries = {}
    with open('src/app/bot/library/field_operators.json', 'r') as file:
        field_operators_json = json.load(file)
    for operator in field_operators_json[name]:
        entries[operator] = field_operators_json[name][operator]['en']['synonyms']
    return Entity(name, entries=entries)


def merge_entities(name: str, entities: list[Entity]):
    entries = {}
    for entity in entities:
        for entry in entity.entries:
            entries[entry.value] = entry.synonyms
    return Entity(name, entries=entries)


def generate_field_value_entity(databot: 'DataBot') -> Entity:
    entries = {}
    for field_schema in databot.project.data_schema.field_schemas:
        if field_schema.categorical:
            for category in field_schema.categories:
                entries[category.value] = category.synonyms['en'].copy()
                databot.field_value_map[category.value] = field_schema.original_name
    return Entity('field_value', entries=entries)


def generate_row_name_entity() -> Entity:
    # TODO: Now only default row names
    entries = {}
    with open('src/app/bot/library/default_row_names.json', 'r') as file:
        row_names_json = json.load(file)
    for row_name in row_names_json['row_name']['en']:
        entries[row_name] = []
    return Entity('row_name', entries=entries)


class DataBotEntities:
    """All the entities used by the DataBot"""

    def __init__(self, databot: 'DataBot'):
        self.numeric_field = databot.bot.add_entity(generate_field_entity(databot, NUMERIC))
        self.textual_field = databot.bot.add_entity(generate_field_entity(databot, TEXTUAL))
        self.datetime_field = databot.bot.add_entity(generate_field_entity(databot, DATETIME))
        # TODO: BOOLEAN field
        self.field = databot.bot.add_entity(generate_field_entity(databot))
        self.numeric_operator = databot.bot.add_entity(generate_operator_entity('numeric_operator'))
        self.textual_operator = databot.bot.add_entity(generate_operator_entity('textual_operator'))
        self.datetime_operator = databot.bot.add_entity(generate_operator_entity('datetime_operator'))
        self.numeric_function_operator = databot.bot.add_entity(generate_operator_entity('numeric_function_operator'))
        self.datetime_function_operator = databot.bot.add_entity(generate_operator_entity('datetime_function_operator'))
        self.function_operator = databot.bot.add_entity(merge_entities('function_operator', [self.numeric_function_operator, self.datetime_function_operator]))
        self.field_value = databot.bot.add_entity(generate_field_value_entity(databot))
        self.row_name = databot.bot.add_entity(generate_row_name_entity())

        # TODO: Field groups
