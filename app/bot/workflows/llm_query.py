import json
import logging
import traceback
from typing import TYPE_CHECKING

from besser.bot.core.session import Session
from openai import OpenAI
from pandasql import sqldf

from app.bot.library.session_keys import LLM_ANSWERS_ENABLED

if TYPE_CHECKING:
    from app.bot.databot import DataBot


class LLMQuery:

    def __init__(self, databot: 'DataBot'):
        self.databot: 'DataBot' = databot
        self.client = None
        self.llm_query = self.databot.bot.new_state('llm_query')

        def llm_query_body(session: Session):
            if self.client and session.get(LLM_ANSWERS_ENABLED):
                try:
                    data_schema_dict = self.databot.project.data_schema.to_dict()
                    response = self.query_openai(session.message, data_schema_dict)
                    if 'sql' in response:
                        df = self.databot.get_df(session)
                        answer = sqldf(response['sql'])
                        self.databot.reply_dataframe(session, answer, response['title'], response['sql'])

                    session.reply('✨ ' + response['answer'])
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
                    You must provide a syntactically correct SQL statement to retrieve the answer to the user question 
                    from the data (the table is called 'df', so use 'FROM df...' in the SQL query).
                    Remember to use column names and values that are present in the data.
                    Do not invent the query parameters. You can guess 
                    some of the query parameters based on the user input (e.g., if there is a 'city' column and the
                    user asks something about 'regions', then you know you should query the 'city' column. Also take a 
                    Consider the following data schema/metadata of the chatbot's csv file if you need it in order to 
                    provide the best answer. Remember there you may find column name synonyms, categories (for 
                    those that are categorical) or type.
                    Your answer must be a valid json with 2 attributes: 'title' (a title for the generated answer), 
                    'sql' (containing the SQL query) and 'answer' 
                    (briefly explaining in natural language how the data was collected, talking in the first person, do 
                    not mention the word SQL)
                    If you consider that the user query is not related to the data, return "I am not an expert in that."
                    as answer and suggest some questions the user could ask about the data.
                    
                    {data_schema}
                    """
                },
                {"role": "user", "content": message},
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)