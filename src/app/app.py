import streamlit as st

from src.app.project import Project
from src.app.speech2text import Speech2Text
from src.utils.session_state_keys import APP, NLP_LANGUAGE, NLP_STT_HF_MODEL, OPENAI_API_KEY, OPENAI_MODEL_NAME


class App:

    def __init__(self):
        self.properties: dict = {
            OPENAI_API_KEY: None,
            OPENAI_MODEL_NAME: 'gpt-4o-mini',
            NLP_LANGUAGE: 'en',  # used for the speech2text component, there is 1 for all the projects
            NLP_STT_HF_MODEL: 'openai/whisper-tiny',
        }
        self.projects: list[Project] = []
        self.speech2text: Speech2Text = Speech2Text(self)

    def add_project(self, project: Project):
        self.projects.append(project)

    def get_project(self, name: str):
        for project in self.projects:
            if project.name == name:
                return project
        return None

    def delete_project(self, project: Project):
        index = self.projects.index(project)
        self.projects.remove(project)
        if self.projects:
            return self.projects[max(index-1, 0)]
        else:
            return None


@st.cache_resource
def create_app():
    _app = App()
    return _app


def get_app():
    if APP not in st.session_state:
        st.session_state[APP] = create_app()
    return st.session_state[APP]
