from io import StringIO

import chardet
import pandas as pd
import requests
import streamlit as st

from app.app import get_app
from app.project import Project
from ui.utils.session_state_keys import ALL_PROJECTS_BUTTON, CKAN, COUNT_CSVS, COUNT_DATASETS, EDITED_PACKAGES_DF, \
    IMPORT, IMPORT_OPEN_DATA_PORTAL, METADATA, NEW_PROJECT_BUTTON, NLP_STT_HF_MODEL, OPENAI_API_KEY, \
    OPEN_DATA_SOURCES, SELECTED_PROJECT, SELECT_ALL_CHECKBOXES, TITLE, UDATA, UPLOAD_DATA
from ui.sidebar import project_selection
from ui.utils.utils import clear_box, disable_input_focusout, get_input_value

st.set_page_config(layout="wide")


def admin():
    """Show the admin container. The different views in the admin page are:

    - New project

    - Project customization

    - All projects
    """
    app = get_app()
    project = st.session_state[SELECTED_PROJECT] if SELECTED_PROJECT in st.session_state else None

    if NEW_PROJECT_BUTTON not in st.session_state:
        st.session_state[NEW_PROJECT_BUTTON] = False
    if ALL_PROJECTS_BUTTON not in st.session_state:
        st.session_state[ALL_PROJECTS_BUTTON] = False
    with st.sidebar:
        project_selection()
        all_projects_button = st.button('All projects')
        new_project_button = st.button('New project')
        if all_projects_button:
            st.session_state[ALL_PROJECTS_BUTTON] = True
            st.session_state[NEW_PROJECT_BUTTON] = False
        if new_project_button:
            st.session_state[ALL_PROJECTS_BUTTON] = False
            st.session_state[NEW_PROJECT_BUTTON] = True
        st.divider()
        st.subheader('Settings')
        app.properties[OPENAI_API_KEY] = st.text_input(
            label='OpenAI API key',
            help='Introduce your OpenAI API key',
            type='password',
            value=app.properties[OPENAI_API_KEY]
        )
        app.properties[NLP_STT_HF_MODEL] = st.text_input(
            label='HuggingFace Speech2Text model',
            help='Introduce a model ID from HuggingFace',
            value=app.properties[NLP_STT_HF_MODEL],
            disabled=True
        )
    if st.session_state[NEW_PROJECT_BUTTON] or not project:
        if st.button('← Go back'):
            st.session_state[ALL_PROJECTS_BUTTON] = False
            st.session_state[NEW_PROJECT_BUTTON] = False
            st.rerun()
        upload_data()
        st.divider()
        import_open_data_portal()
    elif st.session_state[ALL_PROJECTS_BUTTON]:
        # TODO: Cannot click on all projects when in new project
        all_projects_container()
    elif project:
        project_customization_container()


def upload_data():
    """Show the Upload data container."""
    app = get_app()

    st.header('Upload data')
    with st.form(UPLOAD_DATA, clear_on_submit=True):
        project_name = st.text_input(label='Project name', placeholder='Example: sales_project')
        uploaded_file = st.file_uploader(label="Choose a file", type='csv')
        # if uploaded_file is not None:
        submitted = st.form_submit_button(label="Create project", type='primary')
        if submitted:
            if uploaded_file is None:
                st.error('Please add a dataset to the project')
            else:
                if project_name is None or project_name == '':
                    project_name = uploaded_file.name[:-4]  # remove .csv file extension
                project = Project(app, project_name, pd.read_csv(uploaded_file))
                st.session_state[SELECTED_PROJECT] = project
                st.session_state[NEW_PROJECT_BUTTON] = False  # exit the new project UI
                st.rerun()


def import_open_data_portal():
    st.header('Import Open Data portal')

    with st.form(IMPORT_OPEN_DATA_PORTAL, clear_on_submit=False):
        portal_type = st.radio("Select the portal's data management system",
                               [CKAN, UDATA],
                               horizontal=True)
        base_url = st.text_input(label='Base URL', placeholder='Example: http://demo.ckan.org',
                                 value='https://opendata-ajuntament.barcelona.cat/data')  # https://data.london.gov.uk
        # Load all packages
        submitted_base_url = st.form_submit_button(label="Load data sources")
        import_projects = st.form_submit_button(label="Import", type='primary',
                                                disabled=OPEN_DATA_SOURCES not in st.session_state)
    if portal_type == CKAN:
        import_ckan_portal(base_url, submitted_base_url, import_projects)
    else:
        st.error('Currently, only CKAN data management systems are supported')


def import_ckan_portal(base_url: str, submitted_base_url: bool, import_projects: bool):
    app = get_app()
    PACKAGE_LIST_ENDPOINT = '/api/action/package_list'
    PACKAGE_SEARCH_ENDPOINT = '/api/action/package_search'
    if submitted_base_url:
        package_list_url = base_url + PACKAGE_LIST_ENDPOINT
        with st.spinner('Retrieving data sources...'):
            # Get the list of packages
            response = requests.get(package_list_url)
            if response.status_code == 200:
                package_list = response.json()['result']
                package_search_url = base_url + f'{PACKAGE_SEARCH_ENDPOINT}?start=0&rows={len(package_list)}'
                # Get the metadata of all packages
                response = requests.get(package_search_url)
                if response.status_code == 200:
                    packages = response.json()['result']['results']
                    st.session_state[OPEN_DATA_SOURCES] = {}
                    for package in packages:
                        package_name = package['name']
                        st.session_state[OPEN_DATA_SOURCES][package_name] = {
                            TITLE: package['title'],
                            # TODO: ALSO CHECK THE 'format' FIELD IN 'resources': 'CSV'
                            COUNT_CSVS: len(
                                [resource for resource in package['resources'] if resource['name'].endswith('.csv')]),
                            COUNT_DATASETS: len(package['resources']),
                            METADATA: package
                        }
                        # TODO: Now, Set 'Import' to True if it has CSV Data
                        st.session_state[OPEN_DATA_SOURCES][package_name][IMPORT] = True if \
                            st.session_state[OPEN_DATA_SOURCES][package_name][COUNT_CSVS] == 1 else False
                    # Sort the data sources list
                    st.session_state[OPEN_DATA_SOURCES] = dict(
                        sorted(st.session_state[OPEN_DATA_SOURCES].items()))
                    st.rerun()
                else:
                    st.error('Error in package_search')
            else:
                st.error('Error in package_list')

    if OPEN_DATA_SOURCES in st.session_state:  # If packages have been stored in the session...
        if import_projects:
            count_imports = 0
            total_imports = (st.session_state[EDITED_PACKAGES_DF]['Import'] == True).sum()
            import_progress = st.progress(0, text=f'Imported 0/{total_imports} projects')
        st.subheader(f"{len(st.session_state[OPEN_DATA_SOURCES])} packages")
        col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
        # Select/deselect all resources
        with col1:
            if SELECT_ALL_CHECKBOXES not in st.session_state:
                st.session_state[SELECT_ALL_CHECKBOXES] = False

            def update_all_checkboxes():
                st.session_state[SELECT_ALL_CHECKBOXES] = not st.session_state[SELECT_ALL_CHECKBOXES]
                for _, metadata in st.session_state[OPEN_DATA_SOURCES].items():
                    metadata[IMPORT] = st.session_state[SELECT_ALL_CHECKBOXES]

            st.toggle(label="Select all", value=st.session_state[SELECT_ALL_CHECKBOXES],
                      on_change=update_all_checkboxes)
        # Other buttons/toggles...
        with col2:
            pass
        st.info('Only CSV files are supported. Packages without CSV data will not be imported.')
        packages_df = pd.DataFrame(
            [
                {
                    'Import': st.session_state[OPEN_DATA_SOURCES][package][IMPORT],
                    'Name': package,
                    'Title': metadata[TITLE],
                    'Resources': st.session_state[OPEN_DATA_SOURCES][package][COUNT_DATASETS],
                    'CSVs': st.session_state[OPEN_DATA_SOURCES][package][COUNT_CSVS],
                } for package, metadata in st.session_state[OPEN_DATA_SOURCES].items()
            ]
        )
        st.session_state[EDITED_PACKAGES_DF] = st.data_editor(packages_df, use_container_width=True,
                                                                disabled=['Name', 'Title', 'Resources', 'CSVs'])
    if import_projects:
        # Create all projects, download their data
        # Iterate over the edited DataFrame to get the 'Import' boolean value
        for index, row in st.session_state[EDITED_PACKAGES_DF].iterrows():
            if row['Import']:
                package = row['Name']
                metadata = st.session_state[OPEN_DATA_SOURCES][package]
                # TODO: ONLY 1 CSV IN A PACKAGE ALLOWED
                for resource in metadata[METADATA]['resources']:
                    if resource['name'].endswith('.csv'):
                        data_url = resource['url']
                        # Download data
                        response = requests.get(data_url)
                        try:
                            result = chardet.detect(response.content)
                            encoding = result['encoding']
                            df = pd.read_csv(StringIO(response.content.decode(encoding)), low_memory=False)
                            # Create project with the downloaded data into a DataFrame
                            project = Project(app, package, df)
                            count_imports += 1
                            import_progress.progress(count_imports / total_imports,
                                                     text=f'Imported {count_imports}/{total_imports} projects')
                            # TODO: This break forces only 1 csv being downloaded for each package
                            break
                        except Exception as e:
                            st.error(f"Failed to fetch data from {package}")
        st.rerun()


def all_projects_container():
    """Show the All Projects container. It displays a list with all the created projects to easily train/run/stop
    them.
    """
    app = get_app()

    st.header('All projects')
    general_buttons_cols = st.columns([0.15, 0.15, 0.15, 0.15, 0.15, 0.25])
    with general_buttons_cols[0]:
        if st.button('← Go back', use_container_width=True):
            st.session_state[NEW_PROJECT_BUTTON] = False
            st.session_state[ALL_PROJECTS_BUTTON] = False
            st.rerun()
    with general_buttons_cols[1]:
        if st.button('Train All', use_container_width=True, type='primary'):
            with general_buttons_cols[5]:
                count = 0
                progress_bar = st.progress(0, text='Starting training of all projects')
                projects = [p for p in app.projects if not p.bot_running]
                for project in projects:
                    progress_text = f'Training {count + 1}/{len(projects)}: {project.name}'
                    progress_bar.progress(count / len(projects), text=progress_text)
                    project.train_bot()
                    count += 1
                progress_bar.progress(100, text='All projects have been successfully trained!')
    with general_buttons_cols[2]:
        if st.button('Run All', use_container_width=True, type='primary'):
            with general_buttons_cols[5]:
                count = 0
                progress_bar = st.progress(0, text='Running all projects')
                projects = [p for p in app.projects if (p.bot_trained and (not p.bot_running))]
                for project in projects:
                    progress_text = f'Running {count + 1}/{len(projects)}: {project.name}'
                    progress_bar.progress(count / len(projects), text=progress_text)
                    project.run_bot()
                    count += 1
                progress_bar.progress(100, text='All projects are now running !')
    with general_buttons_cols[3]:
        if st.button('Train & Run All', use_container_width=True, type='primary'):
            with general_buttons_cols[5]:
                count = 0
                progress_bar = st.progress(0, text='Training and running all projects')
                projects = [p for p in app.projects if not p.bot_running]
                for project in projects:
                    progress_text = f'Training {count + 1}/{len(projects)}: {project.name}'
                    progress_bar.progress(count / len(projects), text=progress_text)
                    project.train_bot()
                    progress_text = f'Running {count + 1}/{len(projects)}: {project.name}'
                    progress_bar.progress(count / len(projects), text=progress_text)
                    project.run_bot()
                    count += 1
                progress_bar.progress(100, text='All projects trained and running!')
    with general_buttons_cols[4]:
        if st.button('Stop All', use_container_width=True, type='primary'):
            with general_buttons_cols[5]:
                count = 0
                progress_bar = st.progress(0, text='Stopping all projects')
                projects = [p for p in app.projects if p.bot_running]
                for project in projects:
                    progress_text = f'Stopping {count + 1}/{len(projects)}: {project.name}'
                    progress_bar.progress(count / len(projects), text=progress_text)
                    project.stop_bot()
                    count += 1
                progress_bar.progress(100, text='All projects stopped')
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
                st.rerun()


def project_customization_container():
    """Show the Project Customization container."""
    project = st.session_state[SELECTED_PROJECT]
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
    with st.expander(project.name, expanded=False):
        st.dataframe(project.df)
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
                options=[field.original_name for field in project.data_schema.field_schemas],
                label_visibility='collapsed'
            )
    field = project.data_schema.get_field(selected_field)
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
