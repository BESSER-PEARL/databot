import pandas as pd
from besser.bot.core.session import Session
from besser.bot.nlp.intent_classifier.intent_classifier_prediction import IntentClassifierPrediction

from src.app.bot.library import session_keys
from src.app.bot.workflows.abstract_query_workflow import AbstractQueryWorkflow


class FrequentValueInField(AbstractQueryWorkflow):

    def check_params_ok(self, session: Session) -> bool:
        predicted_intent: IntentClassifierPrediction = session.predicted_intent
        field = predicted_intent.get_parameter(session_keys.FIELD).value
        return field

    def answer(self, session: Session) -> None:
        predicted_intent: IntentClassifierPrediction = session.predicted_intent
        df = self.databot.get_df(session)
        field = predicted_intent.get_parameter(session_keys.FIELD).value
        value_counts = df[field].value_counts()
        if predicted_intent.intent == self.databot.intents.most_frequent_value_in_field:
            message_key = 'most_frequent_value_in_field'
            target_value = value_counts.idxmax()
        else:
            message_key = 'least_frequent_value_in_field'
            target_value = value_counts.idxmin()
        self.platform.reply(session, self.databot.messages[message_key].format(field, target_value))
        self.platform.reply(session, self.databot.messages['frequent_value_in_field'].format(field))
        self.databot.reply_dataframe(session, pd.DataFrame(value_counts), f"Count of each different value in '{field}'")
