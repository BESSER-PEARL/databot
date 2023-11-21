from typing import TYPE_CHECKING

import plotly.graph_objs

from app.bot.databot import DataBot
from app.data_source import DataSource
from schema.project_schema import ProjectSchema

if TYPE_CHECKING:
    from app.app import App


class Project:

    def __init__(self, app: 'App', name: str):
        self.app: App = app
        self.name: str = name
        self.databot: DataBot = None
        self.bot_running = False
        self.bot_trained = False
        self.project_schema: ProjectSchema = ProjectSchema(self)
        self.data_sources: list[DataSource] = []

        self.app.add_project(self)
        self.plot: plotly.graph_objs.Figure = None

    def add_data_source(self, data_source: DataSource):
        self.data_sources.append(data_source)

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
