import json
import logging
import random
from typing import TYPE_CHECKING

import pandas as pd
from besser.bot.core.bot import Bot
from besser.bot.core.session import Session
from besser.bot.nlp import NLP_LANGUAGE
from besser.bot.platforms.payload import Payload, PayloadAction
from besser.bot.platforms.websocket import WEBSOCKET_PORT
from besser.bot.platforms.websocket.websocket_platform import WebSocketPlatform
from pandas import DataFrame

from src.app.bot.library.databot_entities import DataBotEntities
from src.app.bot.library.databot_intents import DataBotIntents
from src.app.bot.library.session_keys import FILTERS, LLM_ANSWERS_ENABLED, REPLY_FALLBACK_MESSAGE
from src.app.bot.workflows.llm_query import LLMQuery
from src.app.bot.workflows.queries.charts.area_chart import AreaChart
from src.app.bot.workflows.queries.charts.bar_chart import BarChart
from src.app.bot.workflows.queries.charts.boxplot_chart import BoxplotChart
from src.app.bot.workflows.queries.charts.histogram_chart import HistogramChart
from src.app.bot.workflows.queries.charts.line_chart import LineChart
from src.app.bot.workflows.queries.charts.pie_chart import PieChart
from src.app.bot.workflows.queries.charts.scatter_chart import ScatterChart
from src.app.bot.workflows.queries.tables.field_distinct import FieldDistinct
from src.app.bot.workflows.queries.tables.frequent_value_in_field import FrequentValueInField
from src.app.bot.workflows.queries.tables.select_fields_with_conditions import SelectFieldsWithConditions
from src.app.bot.workflows.queries.tables.value1_vs_value2 import Value1VSValue2
from src.app.bot.workflows.queries.tables.value_frequency import ValueFrequency
from src.schema.field_schema import FieldSchema
from src.schema.filter import Filter
from src.ui.utils.session_state_keys import BOT_DF_DATA, BOT_DF_SQL, BOT_DF_TITLE, SESSION_ID

if TYPE_CHECKING:
    from src.app.project import Project


class DataBot:

    def __init__(self, project: 'Project'):
        self.project: Project = project
        self.bot: Bot = Bot(project.name + '_bot')
        self.field_value_map: dict[str, str] = {}
        self.entities: DataBotEntities = DataBotEntities(self)
        self.intents: DataBotIntents = DataBotIntents(self)
        self.key_fields: list[FieldSchema] = self.project.data_schema.get_key_fields()
        with open('src/app/bot/library/messages.json', 'r', encoding='utf-8') as file:
            self.messages: dict[str, str] = json.load(file)
        logging.basicConfig(level=logging.INFO, format='{levelname} - {asctime}: {message}', style='{')
        self._set_bot_properties()
        self.platform: WebSocketPlatform = self.bot.use_websocket_platform(use_ui=False)

        self.initial = self.bot.new_state('initial', initial=True)
        self.s0 = self.bot.new_state('s0')
        self.llm_query_workflow = LLMQuery(self)

        # Tables
        self.field_distinct = FieldDistinct(self)
        self.frequent_value_in_field = FrequentValueInField(self)
        self.value_frequency = ValueFrequency(self)
        self.value1_vs_value2 = Value1VSValue2(self)
        self.select_fields_with_conditions = SelectFieldsWithConditions(self)

        # Plots/Charts
        self.histogram_chart_workflow = HistogramChart(self)
        self.line_chart_workflow = LineChart(self)
        self.bar_chart_workflow = BarChart(self)
        self.pie_chart_workflow = PieChart(self)
        self.scatter_chart_workflow = ScatterChart(self)
        self.area_chart_workflow = AreaChart(self)
        self.boxplot_chart_workflow = BoxplotChart(self)

        def initial_body(session: Session):
            session.set(FILTERS, [])
            session.set(LLM_ANSWERS_ENABLED, True)
            session.set(REPLY_FALLBACK_MESSAGE, True)
            session.reply(json.dumps({SESSION_ID: session.id}))
            session.reply(self.messages['greetings'].format(self.project.name))

        self.initial.set_body(initial_body)
        self.initial.go_to(self.s0)

        def s0_body(session: Session):
            if not session.get(REPLY_FALLBACK_MESSAGE):
                session.reply(random.choice(self.messages['waiting_user_input']))
            else:
                # After a fallback message, the bot does not reply the "waiting_user_input" message
                session.set(REPLY_FALLBACK_MESSAGE, False)

        self.s0.set_body(s0_body)
        # Plots/Charts
        self.s0.when_intent_matched_go_to(self.intents.histogram_chart, self.histogram_chart_workflow.main_state)
        self.s0.when_intent_matched_go_to(self.intents.line_chart, self.line_chart_workflow.main_state)
        self.s0.when_intent_matched_go_to(self.intents.bar_chart, self.bar_chart_workflow.main_state)
        self.s0.when_intent_matched_go_to(self.intents.pie_chart, self.pie_chart_workflow.main_state)
        self.s0.when_intent_matched_go_to(self.intents.scatter_chart, self.scatter_chart_workflow.main_state)
        self.s0.when_intent_matched_go_to(self.intents.area_chart, self.area_chart_workflow.main_state)
        self.s0.when_intent_matched_go_to(self.intents.boxplot_chart, self.boxplot_chart_workflow.main_state)
        # Tables
        self.s0.when_intent_matched_go_to(self.intents.most_frequent_value_in_field, self.frequent_value_in_field.main_state)
        self.s0.when_intent_matched_go_to(self.intents.least_frequent_value_in_field, self.frequent_value_in_field.main_state)
        self.s0.when_intent_matched_go_to(self.intents.value_frequency, self.value_frequency.main_state)
        self.s0.when_intent_matched_go_to(self.intents.value1_vs_value2, self.value1_vs_value2.main_state)
        self.s0.when_intent_matched_go_to(self.intents.select_fields_with_conditions, self.select_fields_with_conditions.main_state)
        # LLM Fallback
        self.s0.when_no_intent_matched_go_to(self.llm_query_workflow.llm_query)

    def _set_bot_properties(self):
        self.bot.set_property(WEBSOCKET_PORT, self.project.properties[WEBSOCKET_PORT.name])
        self.bot.set_property(NLP_LANGUAGE, self.project.properties[NLP_LANGUAGE.name])

    def get_df(self, session: Session):
        df = self.project.df.copy(deep=True)
        bot_filters: list[Filter] = session.get(FILTERS)
        for bot_filter in bot_filters:
            df = bot_filter.apply(df)
        return df

    def reply_dataframe(self, session: Session, df: DataFrame, title: str, sql: str = None) -> None:
        """Send a DataFrame bot reply, i.e. a table, to a specific user.

        Args:
            title (str): the DataFrame title
            session (Session): the user session
            df (pandas.DataFrame): the message to send to the user
            sql (str): a sql statement if this df has been generated with a sql statement, or None otherwise
        """
        pd.set_option('mode.chained_assignment', None)
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)
        message = {BOT_DF_TITLE: title, BOT_DF_SQL: sql, BOT_DF_DATA: df.to_dict()}
        message = json.dumps(message)
        session.chat_history.append((message, 0))
        payload = Payload(action=PayloadAction.BOT_REPLY_DF,
                          message=message)
        self.platform._send(session.id, payload)
        pd.set_option('mode.chained_assignment', 'warn')

    def reply(self, session: Session, data: DataFrame, title: str, message_key: str):
        if len(data) == 0:
            session.reply(self.messages['nothing_found'].format(title))
        else:
            session.reply(random.choice(self.messages[message_key]).format(title))
