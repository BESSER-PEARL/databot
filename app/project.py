from typing import TYPE_CHECKING

import plotly.graph_objs
from pandas import DataFrame

from app.bot.databot import DataBot
from schema.data_schema import DataSchema

if TYPE_CHECKING:
    from app.app import App


class Project:

    def __init__(self, app: 'App', name: str, df: DataFrame):
        self.app: App = app
        self.name: str = name
        self.databot: DataBot = None
        self.bot_running = False
        self.bot_trained = False
        self.df: DataFrame = df
        self.data_schema: DataSchema = DataSchema(self)
        self.plot: plotly.graph_objs.Figure = None

        self.app.add_project(self)

    def train_bot(self):
        self.databot = DataBot(self)
        self.databot.bot.train()
        self.bot_trained = True

    def run_bot(self):
        self.databot.bot.run(train=False, sleep=False)
        self.bot_running = True

    def stop_bot(self):
        self.bot_running = False
        self.databot.bot.stop()
