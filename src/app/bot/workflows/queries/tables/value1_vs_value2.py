import pandas as pd
from besser.bot.core.session import Session
from besser.bot.nlp.intent_classifier.intent_classifier_prediction import IntentClassifierPrediction

from src.app.bot.library import session_keys
from src.app.bot.workflows.abstract_query_workflow import AbstractQueryWorkflow


class Value1VSValue2(AbstractQueryWorkflow):

    def check_params_ok(self, session: Session) -> bool:
        predicted_intent: IntentClassifierPrediction = session.predicted_intent
        value1 = predicted_intent.get_parameter(session_keys.VALUE + '1').value
        value2 = predicted_intent.get_parameter(session_keys.VALUE + '2').value
        return value1 and value2

    def answer(self, session: Session) -> None:
        predicted_intent: IntentClassifierPrediction = session.predicted_intent
        df = self.databot.get_df(session)
        value1 = predicted_intent.get_parameter(session_keys.VALUE + '1').value
        value2 = predicted_intent.get_parameter(session_keys.VALUE + '2').value
        field1 = self.databot.field_value_map[value1]
        field2 = self.databot.field_value_map[value2]
        count_value1 = len(df[df[field1] == value1])
        count_value2 = len(df[df[field2] == value2])
        message_key = 'value1_more_than_value2'
        if count_value2 > count_value1:
            max_value = value2
            min_value = value1
        else:
            max_value = value1
            min_value = value2
            if count_value2 == count_value1:
                message_key = 'value1_equal_to_value2'
        answer = pd.DataFrame({
            'Value': [value1, value2],
            'Field': [field1, field2],
            'Count': [count_value1, count_value2]
        })
        self.platform.reply(session, self.databot.messages[message_key].format(max_value, min_value))
        self.databot.reply_dataframe(session, answer, f"Frequency of '{value1}' and '{value2}'")
