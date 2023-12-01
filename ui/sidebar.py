import streamlit as st
import streamlit_antd_components as sac

from app.app import get_app
from ui.utils.session_state_keys import SELECTED_PROJECT


def sidebar_menu():
    page = sac.menu([
        sac.MenuItem('Playground', icon='robot'),
        sac.MenuItem('Admin', icon='person-fill'),
        sac.MenuItem('Settings', icon='gear-fill'),
    ], open_all=True)
    return page


def project_selection():
    """Show a project selection container"""
    app = get_app()
    project = st.session_state[SELECTED_PROJECT] if SELECTED_PROJECT in st.session_state else None

    st.subheader('Select a project')
    selected_project = st.selectbox(
        label='Select a project',
        label_visibility='collapsed',
        options=[project.name for project in app.projects],
        index=app.projects.index(project) if project else 0
    )
    st.session_state[SELECTED_PROJECT] = app.get_project(selected_project)
