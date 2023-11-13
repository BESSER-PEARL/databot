import streamlit as st

from app.app import app


def project_selection():
    """Show a project selection container"""
    st.subheader('Select a project')
    selected_project = st.selectbox(
        label='Select a project',
        label_visibility='collapsed',
        options=[project.name for project in app.projects],
        index=app.projects.index(app.selected_project) if app.selected_project else 0
    )
    app.selected_project = app.get_project(selected_project)
