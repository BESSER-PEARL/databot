import pandas as pd
import streamlit as st

from app.project import Project
from app.speech2text import Speech2Text


class App:

    def __init__(self):
        self.properties: dict = {
            'openai_api_key': None,
            'nlp.language': 'en', # used for the speech2text component, there is 1 for all the projects
            'nlp.speech2text.hf.model': 'openai/whisper-tiny',
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


@st.cache_resource
def create_app():
    _app = App()
    if not _app.projects:
        # TESTING PROJECT
        project = Project(_app, 'test_project', pd.read_csv('../datasets/sales.csv'))
    return _app


def get_app():
    if 'app' not in st.session_state:
        st.session_state['app'] = create_app()
    return st.session_state['app']
