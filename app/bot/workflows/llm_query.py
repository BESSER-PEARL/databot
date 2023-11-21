import json
import logging
import traceback
from typing import TYPE_CHECKING

from besser.bot.core.session import Session
from openai import OpenAI


if TYPE_CHECKING:
    from app.bot.databot import DataBot


class LLMQuery:

    def __init__(self, databot: 'DataBot'):
        self.databot: 'DataBot' = databot
        try:
            self.client = OpenAI(api_key=self.databot.project.app.properties['openai_api_key'])
        except Exception as e:
            logging.warning('LLM fallback state will not use OpenAI API, there is no OpenAI API key.')
            self.client = None
        self.llm_query = self.databot.bot.new_state('llm_query')

        def llm_query_body(session: Session):
            if self.client:
                try:
                    data_schema_dict = self.databot.project.data_schema.to_dict()
                    response = self.query_openai(session.message, data_schema_dict)
                    session.reply(str(response))
                except Exception as e:
                    logging.error('An error occurred while calling the OpenAI API. See the attached exception:')
                    traceback.print_exc()
                    session.reply(self.databot.messages['default_fallback_message'])
            else:
                session.reply(self.databot.messages['default_fallback_message'])

        self.llm_query.set_body(llm_query_body)
        self.llm_query.go_to(self.databot.s0)

    def query_openai(self, message: str, data_schema: dict):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    You are a helpful assistant, part of an intent-based chatbot created to answer questions about a 
                    dataset. Your task is to help answering questions the chatbot was not able to identify their intent.
                    Your answer must follow the following json pattern:
                    "answer": "your answer here"
                    Consider the following data schema/metadata of the chatbot's csv file if you need it in order to 
                    provide the best answer.
                    {data_schema}
                    If you consider that the query is not related to the data, answer "I am not an expert in that." and
                    suggest some of questions the user could ask about the data.
                    """
                },
                {"role": "user", "content": message},
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)