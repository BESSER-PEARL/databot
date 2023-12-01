import plotly.express as px
from besser.bot.core.session import Session
from besser.bot.nlp.intent_classifier.intent_classifier_prediction import IntentClassifierPrediction

from app.bot.library import session_keys
from app.bot.workflows.abstract_query_workflow import AbstractQueryWorkflow


class PieChart(AbstractQueryWorkflow):

    def check_params_ok(self, session: Session) -> bool:
        predicted_intent: IntentClassifierPrediction = session.get('predicted_intent')
        field_x = predicted_intent.get_parameter(session_keys.FIELD_X).value
        field_y = predicted_intent.get_parameter(session_keys.FIELD_Y).value
        return field_x and field_y

    def answer(self, session: Session) -> None:
        predicted_intent: IntentClassifierPrediction = session.get('predicted_intent')
        df = self.databot.get_df(session)
        field_x = predicted_intent.get_parameter(session_keys.FIELD_X).value
        field_y = predicted_intent.get_parameter(session_keys.FIELD_Y).value
        fig = px.pie(df, values=field_x, names=field_y, title=f'Pie chart of {field_x} grouped by {field_y}')
        self.platform.reply(session, f'Sure! This is the pie chart of {field_x} grouped by {field_y}')
        self.platform.reply_plotly(session, fig)
