import streamlit as st

from app.app import get_app


def project_selection():
    """Show a project selection container"""
    app = get_app()
    project = st.session_state['selected_project'] if 'selected_project' in st.session_state else None

    st.subheader('Select a project')
    selected_project = st.selectbox(
        label='Select a project',
        label_visibility='collapsed',
        options=[project.name for project in app.projects],
        index=app.projects.index(project) if project else 0
    )
    st.session_state['selected_project'] = app.get_project(selected_project)
