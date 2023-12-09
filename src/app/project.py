from pandas import DataFrame
from typing import TYPE_CHECKING

from src.app.bot.databot import DataBot
from src.schema.data_schema import DataSchema
from src.ui.utils.session_state_keys import NLP_LANGUAGE, WEBSOCKET_PORT

if TYPE_CHECKING:
    from src.app.app import App


class Project:

    def __init__(self, app: 'App', name: str, df: DataFrame):
        self.app: App = app
        self.name: str = name
        self.databot: DataBot = None
        self.bot_running = False
        self.bot_trained = False
        self.df: DataFrame = df  # TODO: list of dataframes? for sources with +1 dataset (e.g. one x year) they must share the same data schema
        self.data_schema: DataSchema = DataSchema(self)
        self.properties: dict = {
            NLP_LANGUAGE: 'en',
            WEBSOCKET_PORT: 8765 + len(self.app.projects)
        }
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
