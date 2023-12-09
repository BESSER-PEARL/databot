import logging
import operator
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from besser.bot.core.session import Session

from src.app.bot.library import session_keys

if TYPE_CHECKING:
    from src.app.bot.databot import DataBot


class AbstractQueryWorkflow(ABC):

    def __init__(self, databot: 'DataBot'):
        self.databot: 'DataBot' = databot

        self.main_state = databot.bot.new_state(self.__class__.__name__)
        self.platform = self.databot.platform

        def check_conditions(session: Session, event_params: dict):
            session_var = session.get(event_params['session_key'])
            func = event_params['func']
            return session_var and func(session)

        def body(session: Session):
            session.set(session_keys.BAD_PARAMS, False)

            if not self.check_params_ok(session):
                session.set(session_keys.BAD_PARAMS, True)
                logging.error('Intent parameters are not OK')
                return
            self.answer(session)

        self.main_state.set_body(body)

        self.main_state.when_variable_matches_operation_go_to(session_keys.BAD_PARAMS, operator.eq, True,
                                                              self.databot.llm_query_workflow.llm_query)
        self.main_state.when_variable_matches_operation_go_to(session_keys.BAD_PARAMS, operator.eq, False,
                                                              self.databot.s0)

    @abstractmethod
    def check_params_ok(self, session: Session) -> bool:
        pass

    @abstractmethod
    def answer(self, session: Session) -> None:
        pass
