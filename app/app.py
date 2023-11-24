import threading

import pandas as pd
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx

from app.project import Project
from app.speech2text import Speech2Text
from ui.session_monitoring import session_monitoring


class App:

    def __init__(self):
        self.properties: dict = {
            'openai_api_key': None,
            'nlp.language': 'en', # used for the speech2text component, there is 1 for all the projects
            'nlp.speech2text.hf.model': 'openai/whisper-tiny',
        }
        self.projects: list[Project] = []
        self.selected_project: Project = None
        self.speech2text: Speech2Text = Speech2Text(self)

    def add_project(self, project: Project):
        self.projects.append(project)

    def get_project(self, name: str):
        for project in self.projects:
            if project.name == name:
                return project
        return None


@st.cache_resource
def get_app():
    _app = App()
    if not _app.projects:
        # TESTING PROJECT
        project = Project(_app, 'test_project', pd.read_csv('../datasets/sales.csv'))
        _app.selected_project = project
    return _app


app = get_app()


@st.cache_data
def run_thread_session_monitoring():
    SESSION_MONITORING_INTERVAL = 3
    session_monitoring_thread = threading.Thread(target=session_monitoring,
                                                 kwargs={'interval': SESSION_MONITORING_INTERVAL})
    add_script_run_ctx(session_monitoring_thread)
    session_monitoring_thread.start()
    return True


run_thread_session_monitoring()
