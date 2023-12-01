import plotly.express as px
from besser.bot.core.session import Session
from besser.bot.nlp.intent_classifier.intent_classifier_prediction import IntentClassifierPrediction

from app.bot.library import session_keys
from app.bot.workflows.abstract_query_workflow import AbstractQueryWorkflow


class BoxplotChart(AbstractQueryWorkflow):

    def check_params_ok(self, session: Session) -> bool:
        predicted_intent: IntentClassifierPrediction = session.get('predicted_intent')
        field = predicted_intent.get_parameter(session_keys.FIELD).value
        return field

    def answer(self, session: Session) -> None:
        predicted_intent: IntentClassifierPrediction = session.get('predicted_intent')
        df = self.databot.get_df(session)
        field = predicted_intent.get_parameter(session_keys.FIELD).value
        fig = px.box(df, y=field, title=f'Boxplot of {field}')
        self.platform.reply(session, f'Sure! This is the boxplot of {field}')
        self.platform.reply_plotly(session, fig)
