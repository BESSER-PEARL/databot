from besser.bot.core.session import Session
from besser.bot.nlp.intent_classifier.intent_classifier_prediction import IntentClassifierPrediction

from app.bot.library import session_keys
from app.bot.workflows.abstract_query_workflow import AbstractQueryWorkflow


class RowCount(AbstractQueryWorkflow):

    def check_params_ok(self, session: Session) -> bool:
        predicted_intent: IntentClassifierPrediction = session.get('predicted_intent')
        row_name = predicted_intent.get_parameter(session_keys.ROW_NAME).value
        return row_name

    def answer(self, session: Session) -> None:
        predicted_intent: IntentClassifierPrediction = session.get('predicted_intent')
        row_name = predicted_intent.get_parameter(session_keys.ROW_NAME).value
        row_count = len(self.databot.project.df)
        self.platform.reply(session, self.databot.messages['show_row_count'].format(row_count, row_name))
