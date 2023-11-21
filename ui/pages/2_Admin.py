import pandas as pd
import streamlit as st

from app.app import app
from app.data_source import DataSource
from app.project import Project
from ui.sidebar import project_selection
from ui.utils.utils import clear_box, disable_input_focusout, get_input_value


def admin():
    """Show the admin container. The different views in the admin page are:

    - New project

    - Project customization

    - All projects
    """
    st.set_page_config(layout="wide")
    if 'new_project_button' not in st.session_state:
        st.session_state['new_project_button'] = False
    if 'all_projects_button' not in st.session_state:
        st.session_state['all_projects_button'] = False
    with st.sidebar:
        project_selection()
        all_projects_button = st.button('All projects')
        new_project_button = st.button('New project')
        st.divider()
        st.subheader('Settings')
        app.properties['openai_api_key'] = st.text_input(
            label='OpenAI API key',
            help='Introduce your OpenAI API key',
            type='password',
            value=app.properties['openai_api_key']
        )
    if new_project_button or st.session_state['new_project_button']:
        st.session_state['new_project_button'] = True  # lock the new project UI
        new_project_container()
    elif all_projects_button or st.session_state['all_projects_button']:
        # TODO: Cannot click on all projects when in new project
        st.session_state['all_projects_button'] = True
        all_projects_container()
    elif app.selected_project:
        project_customization_container()
    else:
        new_project_container()


def new_project_container():
    """Show the New Project container."""
    st.header('New project')
    if st.button('← Go back'):
        st.session_state['new_project_button'] = False  # exit the new project UI
        st.rerun()
    with st.form('new_project', clear_on_submit=True):
        project_name = st.text_input(label='Project name', placeholder='Example: sales_project')
        uploaded_file = st.file_uploader(label="Choose a file", type='csv')
        # if uploaded_file is not None:
        submitted = st.form_submit_button(label="Create project", type='primary')
        if submitted:
            if uploaded_file is None:
                st.error('Please add a dataset to the project')
            else:
                if project_name is None or project_name == '':
                    project_name = f'project_{len(app.projects)}'
                project = Project(app, project_name)
                data_source = DataSource(project, uploaded_file.name, pd.read_csv(uploaded_file))
                app.selected_project = project
                st.session_state['new_project_button'] = False  # exit the new project UI
                st.rerun()


def all_projects_container():
    """Show the All Projects container. It displays a list with all the created projects to easily train/run/stop
    them.
    """
    st.header('All projects')
    general_buttons_cols = st.columns([0.15, 0.15, 0.15, 0.15, 0.15, 0.25])
    with general_buttons_cols[0]:
        if st.button('← Go back', use_container_width=True):
            st.session_state['all_projects_button'] = False  # exit the new project UI
            st.rerun()
    with general_buttons_cols[1]:
        if st.button('Train All', use_container_width=True, type='primary'):
            with general_buttons_cols[5]:
                count = 0
                my_bar = st.progress(0, text='Starting training of all projects')
                projects = [p for p in app.projects if not p.bot_running]
                for project in projects:
                    progress_text = f'Training {count+1}/{len(projects)}: {project.name}'
                    my_bar.progress(count/len(projects), text=progress_text)
                    project.train_bot()
                    count += 1
                my_bar.progress(100, text='All projects have been successfully trained!')
    with general_buttons_cols[2]:
        if st.button('Run All', use_container_width=True, type='primary'):
            with general_buttons_cols[5]:
                count = 0
                my_bar = st.progress(0, text='Running all projects')
                projects = [p for p in app.projects if (p.bot_trained and (not p.bot_running))]
                for project in projects:
                    progress_text = f'Running {count+1}/{len(projects)}: {project.name}'
                    my_bar.progress(count/len(projects), text=progress_text)
                    project.run_bot()
                    count += 1
                my_bar.progress(100, text='All projects are now running !')
    with general_buttons_cols[3]:
        if st.button('Train & Run All', use_container_width=True, type='primary'):
            with general_buttons_cols[5]:
                count = 0
                my_bar = st.progress(0, text='Training and running all projects')
                projects = [p for p in app.projects if not p.bot_running]
                for project in projects:
                    progress_text = f'Training {count + 1}/{len(projects)}: {project.name}'
                    my_bar.progress(count / len(projects), text=progress_text)
                    project.train_bot()
                    progress_text = f'Running {count + 1}/{len(projects)}: {project.name}'
                    my_bar.progress(count / len(projects), text=progress_text)
                    project.run_bot()
                    count += 1
                my_bar.progress(100, text='All projects trained and running!')
    with general_buttons_cols[4]:
        if st.button('Stop All', use_container_width=True, type='primary'):
            with general_buttons_cols[5]:
                count = 0
                my_bar = st.progress(0, text='Stopping all projects')
                projects = [p for p in app.projects if p.bot_running]
                for project in projects:
                    progress_text = f'Stopping {count + 1}/{len(projects)}: {project.name}'
                    my_bar.progress(count / len(projects), text=progress_text)
                    project.stop_bot()
                    count += 1
                my_bar.progress(100, text='All projects stopped')
    for i, project in enumerate(app.projects):
        button_cols = st.columns([0.55, 0.15, 0.15, 0.15])
        with button_cols[0]:
            st.subheader(project.name)
        with button_cols[1]:
            disabled = (not bool(project)) or project.bot_running
            if st.button(
                    key=f'train_{i}',
                    label='Trained' if disabled else 'Train',
                    disabled=bool(disabled),
                    use_container_width=True,
                    type='primary'
            ):
                with st.spinner('Training'):
                    project.train_bot()
        with button_cols[2]:
            disabled = (not bool(project)) or (not project.bot_trained) or project.bot_running
            if st.button(
                    key=f'run_{i}',
                    label='Running' if disabled and project.bot_running else 'Run',
                    disabled=bool(disabled),
                    use_container_width=True,
                    type='primary'
            ):
                project.run_bot()
                st.rerun()
        with button_cols[3]:
            disabled = (not bool(project)) or (not project.bot_running)
            if st.button(
                    key=f'stop_{i}',
                    label='Stop',
                    disabled=bool(disabled),
                    use_container_width=True,
                    type='primary'
            ):
                project.stop_bot()
                # del st.session_state['history']
                # del st.session_state['queue']
                st.rerun()


def project_customization_container():
    """Show the Project Customization container."""
    project = app.selected_project
    st.header(f'Project: {project.name}')
    # TRAIN/RUN/STOP BUTTONS
    col1, col2, col3, col4 = st.columns([0.15, 0.15, 0.15, 0.55])
    with col1:
        disabled = (not bool(project)) or project.bot_running
        if st.button(
                key='train',
                label='Trained' if disabled else 'Train',
                disabled=bool(disabled),
                use_container_width=True,
                type='primary'
        ):
            with st.spinner('Training...'):
                project.train_bot()
    with col2:
        disabled = (not bool(project)) or (not project.bot_trained) or project.bot_running
        if st.button(
                key='run',
                label='Running' if disabled and project.bot_running else 'Run',
                disabled=bool(disabled),
                use_container_width=True,
                type='primary'
        ):
            project.run_bot()
            st.rerun()
    with col3:
        disabled = (not bool(project)) or (not project.bot_running)
        if st.button(
                key='stop',
                label='Stop',
                disabled=bool(disabled),
                use_container_width=True,
                type='primary'
        ):
            project.stop_bot()
            # del st.session_state['history']
            # del st.session_state['queue']
            st.rerun()
    with col4:
        if project.bot_running:
            st.info('The bot is running. You can switch to the Playground and start using it!', icon="✅")
        elif project.bot_trained:
            st.info('The bot has been trained successfully, now you can run it!', icon="✅")
        else:
            st.info('You need to train the bot before using it in the Playground', icon="❓")

    # DATA PREVIEW
    st.subheader('Data preview')
    data_source = project.data_sources[0]
    with st.expander(data_source.name, expanded=False):
        st.dataframe(data_source.df)
    # FIELD CUSTOMIZATION
    st.subheader('Data schema')
    st.info(
        body='The data schema is what the bot reads to study your project and be able to:\n'
             '- Understand your questions\n'
             '- Produce quality answers\n\n'
             'You should review the automatically generated data schema and complete it if you find it '
             'necessary',
        icon='💡')
    col1, col2, col3 = st.columns([0.2, 0.4, 0.4])
    with col1:
        with st.expander('Select a field', expanded=True):
            selected_field = st.radio(
                label='selected_field',
                options=[field.original_name for field in data_source.data_schema.field_schemas],
                label_visibility='collapsed'
            )
    field = data_source.get_field(selected_field)
    with col2:
        # READABLE NAME
        field.readable_name = st.text_input(
            label='Readable name',
            value=field.readable_name,
            help='If the field name is strange, too long or unrepresentative, '
                 'you can choose a better one to replace it.'
        )
        # SYNONYMS
        st.text_input(
            label='Add synonym',
            help='You can add synonyms to the field name',
            on_change=clear_box,
            key='field_synonym',
            args=['field_synonym']
        )
        synonym = get_input_value('field_synonym')
        if synonym and synonym not in field.synonyms['en']:
            field.synonyms['en'].append(synonym)
        with st.expander('All synonyms', expanded=len(field.synonyms['en']) > 0):
            if field.synonyms['en']:
                delete_synonyms = []
                for s in field.synonyms['en']:
                    selected = st.checkbox(s)
                    if selected:
                        delete_synonyms.append(s)
                if st.button(label='Delete', key='delete_field_synonym'):
                    for s in delete_synonyms:
                        field.synonyms['en'].remove(s)
                    st.rerun()
            else:
                st.error('There are no synonyms')
        # TYPE
        st.text_input(
            label='Field type',
            value=field.type.t,
            disabled=True
        )
        # NUM DIFFERENT VALUES
        st.text_input(
            label='Number of different values',
            value=field.num_different_values,
            disabled=True
        )
        # CATEGORICAL
        field.categorical = st.toggle(
            label='Categorical',
            value=field.categorical
        )
        # KEY
        field.key = st.toggle(
            label='Key',
            value=field.key
        )
        # TAGS
        field.tags = st.multiselect(
            label='Tags',
            options=['money', 'birthdate', 'city', 'salary', 'gender'],
        )

    with col3:
        st.text('Field categories')
        selected_category = st.selectbox(
            label='Select a category',
            options=[c.value for c in field.categories] if field.categories else [],
            disabled=not field.categorical
        )
        st.text_input(
            label='Add synonym',
            help='You can add synonyms to the field category',
            disabled=not field.categorical,
            on_change=clear_box,
            key='category_synonym',
            args=['category_synonym']
        )
        if not field.categorical:
            st.error('To see the field categories you must set this field as categorical')
        else:
            category = field.get_category(selected_category)
            synonym = get_input_value('category_synonym')
            if synonym and synonym not in category.synonyms['en']:
                category.synonyms['en'].append(synonym)
            if category.synonyms['en']:
                delete_synonyms = []
                for s in category.synonyms['en']:
                    selected = st.checkbox(s)
                    if selected:
                        delete_synonyms.append(s)
                if st.button(label='Delete', key='delete_category_synonym'):
                    for s in delete_synonyms:
                        category.synonyms['en'].remove(s)
                    st.rerun()
            else:
                st.error('There are no synonyms')


# Run it to display the Admin page
admin()
disable_input_focusout()
