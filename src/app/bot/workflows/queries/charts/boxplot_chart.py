import plotly.express as px
from besser.bot.core.session import Session
from besser.bot.nlp.intent_classifier.intent_classifier_prediction import IntentClassifierPrediction

from src.app.bot.library import session_keys
from src.app.bot.workflows.abstract_query_workflow import AbstractQueryWorkflow


class BoxplotChart(AbstractQueryWorkflow):

    def check_params_ok(self, session: Session) -> bool:
        predicted_intent: IntentClassifierPrediction = session.predicted_intent
        field = predicted_intent.get_parameter(session_keys.FIELD).value
        return field

    def answer(self, session: Session) -> None:
        predicted_intent: IntentClassifierPrediction = session.predicted_intent
        df = self.databot.get_df(session)
        field = predicted_intent.get_parameter(session_keys.FIELD).value
        title = f'Boxplot of {field}'
        fig = px.box(df, y=field, title=title)
        self.databot.reply(session, df, title, 'plot_message')
        self.platform.reply_plotly(session, fig)
