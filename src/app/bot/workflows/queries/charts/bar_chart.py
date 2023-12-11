import plotly.express as px
from besser.bot.core.session import Session
from besser.bot.nlp.intent_classifier.intent_classifier_prediction import IntentClassifierPrediction

from src.app.bot.library import session_keys
from src.app.bot.workflows.abstract_query_workflow import AbstractQueryWorkflow


class BarChart(AbstractQueryWorkflow):

    def check_params_ok(self, session: Session) -> bool:
        predicted_intent: IntentClassifierPrediction = session.predicted_intent
        field_x = predicted_intent.get_parameter(session_keys.FIELD_X).value
        field_y = predicted_intent.get_parameter(session_keys.FIELD_Y).value
        return field_x and field_y

    def answer(self, session: Session) -> None:
        predicted_intent: IntentClassifierPrediction = session.predicted_intent
        df = self.databot.get_df(session)
        field_x = predicted_intent.get_parameter(session_keys.FIELD_X).value
        field_y = predicted_intent.get_parameter(session_keys.FIELD_Y).value
        title = f'Bar chart of {field_y} grouped by {field_x}'
        fig = px.bar(df, x=field_x, y=field_y, title=title)
        self.databot.reply(session, df, title, 'plot_message')
        self.platform.reply_plotly(session, fig)
