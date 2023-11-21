from typing import TYPE_CHECKING

from besser.bot.core.intent.intent import Intent
from besser.bot.core.session import Session
from besser.bot.nlp.intent_classifier.intent_classifier_prediction import IntentClassifierPrediction

if TYPE_CHECKING:
    from app.bot.databot import DataBot


class CheckParameters:

    def __init__(self, databot: 'DataBot'):
        self.databot: 'DataBot' = databot
        self.check_parameters = self.databot.bot.new_state('check_parameters')

        def check_intent(session: Session, event_params: dict):
            predicted_intent: Intent = session.get('predicted_intent').intent
            target_intent: Intent = event_params['intent']
            return predicted_intent.name == target_intent.name

        def check_parameters_body(session: Session):
            predicted_intent: IntentClassifierPrediction = session.predicted_intent
            # session.reply(f'I detected the intent {predicted_intent.intent.name}')
            # session.reply(f'Parameters: {[(mp.name, mp.value) for mp in predicted_intent.matched_parameters]}')
            session.set('predicted_intent', predicted_intent)

        self.check_parameters.set_body(check_parameters_body)
        self.check_parameters.when_event_go_to(check_intent, self.databot.s0, event_params={'intent': self.databot.intents.show_field_distinct})
        self.check_parameters.when_event_go_to(check_intent, self.databot.s0, event_params={'intent': self.databot.intents.most_frequent_value_in_field})
        self.check_parameters.when_event_go_to(check_intent, self.databot.s0, event_params={'intent': self.databot.intents.least_frequent_value_in_field})
        self.check_parameters.when_event_go_to(check_intent, self.databot.s0, event_params={'intent': self.databot.intents.value_frequency})
        self.check_parameters.when_event_go_to(check_intent, self.databot.s0, event_params={'intent': self.databot.intents.value1_more_than_value2})
        self.check_parameters.when_event_go_to(check_intent, self.databot.s0, event_params={'intent': self.databot.intents.value1_less_than_value2})
        self.check_parameters.when_event_go_to(check_intent, self.databot.row_count_workflow.main_state, event_params={'intent': self.databot.intents.row_count})
        self.check_parameters.when_event_go_to(check_intent, self.databot.s0, event_params={'intent': self.databot.intents.field_count})
        self.check_parameters.when_event_go_to(check_intent, self.databot.s0, event_params={'intent': self.databot.intents.select_fields_with_conditions})
        self.check_parameters.when_event_go_to(check_intent, self.databot.s0, event_params={'intent': self.databot.intents.numeric_field_operator_value})
        self.check_parameters.when_event_go_to(check_intent, self.databot.s0, event_params={'intent': self.databot.intents.datetime_field_operator_value})
        self.check_parameters.when_event_go_to(check_intent, self.databot.s0, event_params={'intent': self.databot.intents.textual_field_operator_value})
        self.check_parameters.when_event_go_to(check_intent, self.databot.s0, event_params={'intent': self.databot.intents.numeric_field_between_values})
        self.check_parameters.when_event_go_to(check_intent, self.databot.s0, event_params={'intent': self.databot.intents.datetime_field_between_values})


        self.check_parameters.when_event_go_to(check_intent, self.databot.histogram_chart_workflow.main_state, event_params={'intent': self.databot.intents.histogram_chart})
        self.check_parameters.when_event_go_to(check_intent, self.databot.line_chart_workflow.main_state, event_params={'intent': self.databot.intents.line_chart})
        self.check_parameters.when_event_go_to(check_intent, self.databot.bar_chart_workflow.main_state, event_params={'intent': self.databot.intents.bar_chart})
