import threading

import pandas as pd
from streamlit.runtime.scriptrunner import add_script_run_ctx

from app.data_source import DataSource
from app.project import Project
from ui.session_monitoring import session_monitoring


class App:

    def __init__(self):
        self.projects: list[Project] = []
        self.selected_project: Project = None
        self.properties: dict = {
            'openai_api_key': None,
        }
        print('nueva app creadaaaa')

    def add_project(self, project: Project):
        self.projects.append(project)

    def get_project(self, name: str):
        for project in self.projects:
            if project.name == name:
                return project
        return None


app = App()
if not app.projects:
    # TESTING PROJECT
    project = Project(app, 'test_project')
    data_source = DataSource(project, 'sales.csv', pd.read_csv('../sales.csv'))
    app.selected_project = project

print('running session monitoring thread!!!!')
SESSION_MONITORING_INTERVAL = 3
session_monitoring_thread = threading.Thread(target=session_monitoring,
                                             kwargs={'interval': SESSION_MONITORING_INTERVAL})
add_script_run_ctx(session_monitoring_thread)
session_monitoring_thread.start()
