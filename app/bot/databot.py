import json
import logging
from typing import TYPE_CHECKING

from besser.bot.core.bot import Bot
from besser.bot.core.session import Session
from besser.bot.nlp.intent_classifier.intent_classifier_prediction import IntentClassifierPrediction
from besser.bot.platforms.websocket.websocket_platform import WebSocketPlatform

from app.bot.library.databot_entities import DataBotEntities
from app.bot.library.databot_intents import DataBotIntents
from app.bot.workflows.check_parameters import CheckParameters
from app.bot.workflows.llm_query import LLMQuery
from app.bot.workflows.queries.bar_chart import BarChart
from app.bot.workflows.queries.histogram_chart import HistogramChart
from app.bot.workflows.queries.line_chart import LineChart
from app.bot.workflows.queries.row_count import RowCount

if TYPE_CHECKING:
    from app.project import Project


class DataBot:

    def __init__(self, project: 'Project'):
        self.project: Project = project
        self.bot: Bot = Bot(project.name + '_bot')
        self.field_value_map: dict[str, str] = {}
        self.entities: DataBotEntities = DataBotEntities(self)
        self.intents: DataBotIntents = DataBotIntents(self)
        with open('../app/bot/library/messages.json', 'r', encoding='utf-8') as file:
            self.messages: dict[str, str] = json.load(file)
        logging.basicConfig(level=logging.INFO, format='{levelname} - {asctime}: {message}', style='{')
        self._set_bot_properties()
        self.platform: WebSocketPlatform = self.bot.use_websocket_platform(use_ui=False)

        self.initial = self.bot.new_state('initial', initial=True)
        self.s0 = self.bot.new_state('s0')
        self.llm_query_workflow = LLMQuery(self)
        self.row_count_workflow = RowCount(self)
        self.histogram_chart_workflow = HistogramChart(self)
        self.line_chart_workflow = LineChart(self)
        self.bar_chart_workflow = BarChart(self)
        self.check_parameters_workflow = CheckParameters(self)

        def initial_body(session: Session):
            session.reply(self.messages['greetings'])

        self.initial.set_body(initial_body)
        self.initial.go_to(self.s0)

        def s0_body(session: Session):
            session.reply(self.messages['select_action'])

        self.s0.set_body(s0_body)
        # self.s0.when_intent_matched_go_to(self.intents.show_field_distinct, self.check_parameters)
        # self.s0.when_intent_matched_go_to(self.intents.most_frequent_value_in_field, self.check_parameters)
        # self.s0.when_intent_matched_go_to(self.intents.least_frequent_value_in_field, self.check_parameters)
        # self.s0.when_intent_matched_go_to(self.intents.value_frequency, self.check_parameters)
        # self.s0.when_intent_matched_go_to(self.intents.value1_more_than_value2, self.check_parameters)
        # self.s0.when_intent_matched_go_to(self.intents.value1_less_than_value2, self.check_parameters)
        self.s0.when_intent_matched_go_to(self.intents.row_count, self.check_parameters_workflow.check_parameters)
        # self.s0.when_intent_matched_go_to(self.intents.field_count, self.check_parameters)
        # self.s0.when_intent_matched_go_to(self.intents.select_fields_with_conditions, self.check_parameters)
        # self.s0.when_intent_matched_go_to(self.intents.numeric_field_operator_value, self.check_parameters)
        # self.s0.when_intent_matched_go_to(self.intents.datetime_field_operator_value, self.check_parameters)
        # self.s0.when_intent_matched_go_to(self.intents.textual_field_operator_value, self.check_parameters)
        # self.s0.when_intent_matched_go_to(self.intents.numeric_field_between_values, self.check_parameters)
        # self.s0.when_intent_matched_go_to(self.intents.datetime_field_between_values, self.check_parameters)
        self.s0.when_intent_matched_go_to(self.intents.histogram_chart, self.check_parameters_workflow.check_parameters)
        self.s0.when_intent_matched_go_to(self.intents.line_chart, self.check_parameters_workflow.check_parameters)
        self.s0.when_intent_matched_go_to(self.intents.bar_chart, self.check_parameters_workflow.check_parameters)
        self.s0.when_no_intent_matched_go_to(self.llm_query_workflow.llm_query)








    def _set_bot_properties(self):
        pass

