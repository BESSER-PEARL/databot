from typing import TYPE_CHECKING

import besser.bot.test.examples.weather_bot as weather_bot

from besser.bot.core.bot import Bot

from app.data_source import DataSource
from schema.project_schema import ProjectSchema

if TYPE_CHECKING:
    from app.app import App


class Project:

    def __init__(self, app: 'App', name: str):
        self.app: App = app
        self.name: str = name
        self.bot: Bot = weather_bot.bot
        self.bot_running = False
        self.bot_trained = False
        self.project_schema: ProjectSchema = ProjectSchema(self)
        self.data_sources: list[DataSource] = []

        self.app.add_project(self)

    def add_data_source(self, data_source: DataSource):
        self.data_sources.append(data_source)

    def train_bot(self):
        self._generate_bot()
        self.bot.train()
        self.bot_trained = True

    def run_bot(self):
        self.bot._platforms[0]._use_ui = False
        self.bot_running = True
        self.bot.run(train=False, sleep=False)

    def stop_bot(self):
        self.bot_running = False
        self.bot.stop()

    def _generate_bot(self):
        # GENERATE BOT BASED ON SCHEMA
        pass
