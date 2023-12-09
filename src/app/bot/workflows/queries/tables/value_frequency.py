from besser.bot.core.session import Session
from besser.bot.nlp.intent_classifier.intent_classifier_prediction import IntentClassifierPrediction

from src.app.bot.library import session_keys
from src.app.bot.workflows.abstract_query_workflow import AbstractQueryWorkflow


class ValueFrequency(AbstractQueryWorkflow):

    def check_params_ok(self, session: Session) -> bool:
        predicted_intent: IntentClassifierPrediction = session.predicted_intent
        value = predicted_intent.get_parameter(session_keys.VALUE).value
        return value

    def answer(self, session: Session) -> None:
        predicted_intent: IntentClassifierPrediction = session.predicted_intent
        df = self.databot.get_df(session)
        value = predicted_intent.get_parameter(session_keys.VALUE).value
        field = self.databot.field_value_map[value]
        answer = df[df[field] == value]
        self.platform.reply(session, self.databot.messages['value_frequency'].format(len(answer), field, value))
        self.databot.reply_dataframe(session, answer, f"Records with {field} = '{value}'")
