from typing import TYPE_CHECKING

from besser.bot.core.session import Session

if TYPE_CHECKING:

    from app.bot.databot import DataBot


class ShowResult:

    def __init__(self, databot: 'DataBot'):
        self.databot: 'DataBot' = databot
        self.show_table = databot.bot.new_state('show_table')

        def show_table_body(session: Session):
            session.reply('here I should display a table')
            pass

        self.show_table.set_body(show_table_body)
        self.show_table.go_to(self.databot.s0)