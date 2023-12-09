import pandas as pd
from besser.bot.core.session import Session
from besser.bot.nlp.intent_classifier.intent_classifier_prediction import IntentClassifierPrediction
from besser.bot.nlp.ner.matched_parameter import MatchedParameter

from src.app.bot.library import session_keys
from src.app.bot.workflows.abstract_query_workflow import AbstractQueryWorkflow

AVG = 'avg'
SUM = 'sum'
MAX = 'max'
MIN = 'min'
OLDEST = 'oldest'
NEWEST = 'newest'
DEFAULT_NUMBER = 1


def get_number_or_default(number):
    if not number:
        number = DEFAULT_NUMBER
    return int(number)


def max_min_oldest_newest(operator: str):
    return operator and max_min(operator) or oldest_newest(operator)


def max_min(operator: str):
    return operator and (operator == MAX or operator == MIN)


def oldest_newest(operator: str):
    return operator and (operator == OLDEST or operator == NEWEST)


def datetime_operator_to_numeric_operator(operator: str):
    if operator == OLDEST:
        return MIN
    elif operator == NEWEST:
        return MAX
    return operator


def get_operator_field(operator: str, field1: str, field2: str):
    if operator:
        if field1 and field2:
            # Give me the FIELD1 with the highest FIELD2...
            # Give me the targetField with the highest operatorField
            return field2
        else:
            # Give me the highest FIELD1...
            # Give me the highest operatorField
            return field1
    return None


def get_target_field(operator: str, field1: str, field2: str):
    if operator:
        if field1 and field2:
            # Give me the FIELD1 with the highest FIELD2...
            # Give me the targetField with the highest operatorField
            return field1
        else:
            # Give me the highest FIELD1...
            # Give me the highest operatorField
            return None
    # Give me the FIELD1 of VALUE => Give me the targetField of VALUE
    # Give me the ROW_NAME of VALUE => NULL
    return field1


class SelectFieldsWithConditions(AbstractQueryWorkflow):

    def get_select_fields(self, key_fields: list[str], value_field_map: dict[str, str], target_field: str,
                          operator_field: str):
        select_fields = []
        if key_fields is not None:
            select_fields.extend(key_fields)
        if value_field_map is not None:
            select_fields.extend(value_field_map.values())
        if target_field:
            select_fields.append(target_field)
        if operator_field:
            select_fields.append(operator_field)
        select_fields = list(set(select_fields))
        # Get the selected fields in the original order
        return [field for field in self.databot.project.df.columns.tolist() if field in select_fields]

    def get_value_field_map(self, *values):
        value_field_map = {}
        for value in values:
            if value:
                value_field_map[value] = self.databot.field_value_map[value]
        return value_field_map

    def check_params_ok(self, session: Session) -> bool:
        predicted_intent: IntentClassifierPrediction = session.predicted_intent
        number = predicted_intent.get_parameter(session_keys.NUMBER).value
        field1 = predicted_intent.get_parameter(session_keys.FIELD + '1').value
        row_name = predicted_intent.get_parameter(session_keys.ROW_NAME).value
        operator = predicted_intent.get_parameter(session_keys.OPERATOR).value
        field2 = predicted_intent.get_parameter(session_keys.FIELD + '2').value
        value1 = predicted_intent.get_parameter(session_keys.VALUE + '1').value
        value2 = predicted_intent.get_parameter(session_keys.VALUE + '2').value

        operator_field = get_operator_field(operator, field1, field2)
        if (operator is None) != (operator_field is None):
            # We should have both operator and operatorField or none of them
            return False

        if operator and \
                not (operator in [e.value for e in self.databot.entities.numeric_function_operator.entries] and operator_field in [e.value for e in self.databot.entities.numeric_field.entries]) and \
                not (operator in [e.value for e in self.databot.entities.datetime_function_operator.entries] and operator_field in [e.value for e in self.databot.entities.datetime_field.entries]):
            # Check that operator type matches operatorField type
            return False

        value_field_map = self.get_value_field_map(value1, value2)
        session.set(session_keys.VALUE_FIELD_MAP, value_field_map)
        some_value = len(value_field_map) > 0

        if some_value and (not number) and (not row_name) and (not field1) and (not operator) and (not field2):
            # Who are the VALUE?
            # Who are the women?
            predicted_intent.matched_parameters.append(MatchedParameter(session_keys.ROW_NAME, self.databot.entities.row_name.entries[0].value, {}))
            # We store a rowName, since this is the same as "Give me the rows that are woman"
            return True

        if row_name and some_value and (not number) and (not field1) and (not operator) and (not field2):
            # Give me the ROW_NAME of VALUE
            # Give me the members of marketing
            return True

        if field1 and some_value and (not number) and (not row_name) and (not operator) and (not field2):
            # Give me the FIELD1 of VALUE
            # Give me the salaries of marketing
            return True

        if operator and field1 and (not row_name) and (not field2):
            # Give me the [NUMBER] OPERATOR FIELD1 [of VALUE]
            # Give me the [5] highest salary [of marketing]
            return True

        if field1 and operator and field2 and (not row_name):
            # Give me the [NUMBER] FIELD1 with the OPERATOR FIELD2 [of VALUE]
            # Give me the [5] ages with the highest salary [of marketing]
            return True

        if row_name and operator and field1 and (not field2):
            # Give me the [NUMBER] ROW_NAME with the OPERATOR FIELD1 [of VALUE]
            # Give me the [5] members with the highest salary [of marketing]
            return True

        # At this point, we have not found a valid combination of parameters
        return False

    def answer(self, session: Session) -> None:
        predicted_intent: IntentClassifierPrediction = session.predicted_intent
        df = self.databot.get_df(session)
        number = predicted_intent.get_parameter(session_keys.NUMBER).value
        field1 = predicted_intent.get_parameter(session_keys.FIELD + '1').value
        operator = predicted_intent.get_parameter(session_keys.OPERATOR).value
        field2 = predicted_intent.get_parameter(session_keys.FIELD + '2').value
        value_field_map = session.get(session_keys.VALUE_FIELD_MAP)

        operator_field = get_operator_field(operator, field1, field2)
        target_field = get_target_field(operator, field1, field2)
        key_fields = [field.original_name for field in self.databot.key_fields]
        if not key_fields:
            key_fields = [field.original_name for field in self.databot.project.data_schema.field_schemas]

        title = ''
        if not operator:
            # SELECT fields WHERE conditions
            select_fields = self.get_select_fields(key_fields, value_field_map, target_field, None)
            for v, f in value_field_map.items():
                df = df[df[f] == v]
                title += f', {f} = {v}'
            title = title[2:]
            df = df[select_fields]

        elif max_min_oldest_newest(operator):
            # SELECT fields, MAX(operatorField) WHERE conditions
            select_fields = self.get_select_fields(key_fields, value_field_map, target_field, operator_field)
            # if we have a datetime operator (oldest/newest), convert it to numeric operator (min/max)
            operator = datetime_operator_to_numeric_operator(operator)
            number = get_number_or_default(number)
            for v, f in value_field_map.items():
                df = df[df[f] == v]
                title += f', {f} = {v}'
            if operator == MAX:
                df = df.nlargest(number, operator_field, keep='all')
                title = f'highest {operator_field}' + title
            elif operator == MIN:
                df = df.nsmallest(number, operator_field, keep='all')
                title = f'lowest {operator_field}' + title
            if number > 1:
                title = f'Top {number} ' + title
            df = df[select_fields]

        else:
            # Other operators (AVG, SUM)
            # SELECT AVG(operatorField) WHERE conditions
            answer = pd.DataFrame()
            for v, f in value_field_map.items():
                df = df[df[f] == v]
                answer[f] = [v]
                title += f', {f} = {v}'
            if operator == AVG:
                answer[f'Average {operator_field}'] = [df[operator_field].mean()]
                title = f'Average {operator_field}' + title
            elif operator == SUM:
                answer[f'Total {operator_field}'] = [df[operator_field].sum()]
                title = f'Total {operator_field}' + title
            df = answer

        if target_field:
            title = f'{target_field} with ' + title

        self.databot.reply(session, df, title, 'table_message')
        self.databot.reply_dataframe(session, df, title)
