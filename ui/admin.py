import concurrent.futures
import threading
import time
from io import StringIO

import chardet
import pandas as pd
import requests
import streamlit as st
import streamlit_antd_components as sac
from streamlit.runtime.scriptrunner import add_script_run_ctx

from app.app import get_app
from app.project import Project
from schema.field_type import BOOLEAN, DATETIME, NUMERIC, TEXTUAL
from ui.utils.session_state_keys import CKAN, COUNT_CSVS, COUNT_DATASETS, EDITED_PACKAGES_DF, \
    IMPORT, IMPORT_OPEN_DATA_PORTAL, METADATA, OPEN_DATA_SOURCES, SELECTED_PROJECT, SELECT_ALL_CHECKBOXES, TITLE, \
    UDATA, UPLOAD_DATA
from ui.sidebar import admin_menu
from ui.utils.utils import clear_box, get_input_value, project_selection


def admin():
    """Show the admin container. The different views in the admin page are:

    - New project

    - Manage project

    - All projects
    """
    project = st.session_state[SELECTED_PROJECT] if SELECTED_PROJECT in st.session_state else None

    with st.sidebar:
        admin_page = admin_menu()

    if admin_page == 'New project' or not project:
        upload_data()
        st.divider()
        import_open_data_portal()
    elif admin_page == 'All projects':
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
                if project_name in [project.name for project in app.projects]:
                    st.error(f"The project name '{project_name}' already exists. Please choose another one")
                else:
                    project = Project(app, project_name, pd.read_csv(uploaded_file))
                    st.session_state[SELECTED_PROJECT] = project
                    st.info(f'The project **{project.name}** has been created! Go to **Manage project** to train a 🤖 bot upon it.')
                    if len(app.projects) == 1:
                        # If first project, rerun
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
            finish_message = st.empty()
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
        start_time = time.time()
        lock = threading.Lock()  # Create a lock for thread safety
        projects = []

        def download_and_process(package, resource, c=0):
            if c > 500:
                st.error(f"Failed to download {package}. Maximum number of attempts exceeded.")
                return
            try:
                data_url = resource['url']
                # Download data
                response = requests.get(data_url)
                if response.status_code == 503:
                    # Retrying download
                    download_and_process(package, resource, c+1)
                    return
                else:
                    result = chardet.detect(response.content)
                    encoding = result['encoding']
                    df = pd.read_csv(StringIO(response.content.decode(encoding)), low_memory=False)
                    # Update progress bar
                    with lock:
                        nonlocal count_imports
                        count_imports += 1
                        import_progress.progress(count_imports / total_imports,
                                                 text=f'Imported {count_imports}/{total_imports} projects')
                        projects.append((package, df))

            except Exception as e:
                print(f"Failed to fetch data from {package}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            # Use executor.map to parallelize the downloads
            futures = []
            for index, row in st.session_state[EDITED_PACKAGES_DF].iterrows():
                if row['Import']:
                    package = row['Name']
                    metadata = st.session_state[OPEN_DATA_SOURCES][package]
                    for resource in metadata[METADATA]['resources']:
                        if resource['name'].endswith('.csv'):
                            future = executor.submit(download_and_process, package, resource, 0)
                            futures.append(future)
                            break
            for t in executor._threads:
                add_script_run_ctx(t)

        concurrent.futures.wait(futures)
        for i, p in enumerate(sorted(projects, key=lambda x: x[0])):
            project = Project(app, p[0], p[1])
            if i == 0:
                st.session_state[SELECTED_PROJECT] = project

        # Wait for all futures to complete
        concurrent.futures.wait(futures)
        end_time = time.time()
        elapsed_time_seconds = end_time - start_time
        elapsed_hours = int(elapsed_time_seconds // 3600)
        elapsed_minutes = int(elapsed_time_seconds // 60)
        remaining_seconds = elapsed_time_seconds % 60
        finish_message.info(f"Importing data finished. Elapsed Time: {elapsed_hours}:{elapsed_minutes}:{remaining_seconds:.3f}")


def all_projects_container():
    """Show the All Projects container. It displays a list with all the created projects to easily train/run/stop
    them.
    """
    app = get_app()

    st.header('All projects')
    general_buttons_cols = st.columns([0.1, 0.1, 0.13, 0.1, 0.12, 0.45])
    with general_buttons_cols[5]:
        progress_bar = st.progress(0, '')

    def run_something(funcs, total, action, *args):
        for f in funcs:
            f(args)
        with lock:
            nonlocal count
            count += 1
            progress_bar.progress(count / total,
                                  text=f'{action} {count}/{total} project bots')

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Use executor.map to parallelize the downloads
        futures = []
        lock = threading.Lock()  # Create a lock for thread safety
        count = 0
        with general_buttons_cols[0]:
            if st.button('Train All', use_container_width=True, type='primary'):
                projects = [p for p in app.projects if not p.bot_running]
                for project in projects:
                    future = executor.submit(run_something, [project.train_bot], len(projects), 'Trained')
                    futures.append(future)

        with general_buttons_cols[1]:
            if st.button('Run All', use_container_width=True, type='primary'):
                projects = [p for p in app.projects if (p.bot_trained and (not p.bot_running))]
                for project in projects:
                    future = executor.submit(run_something, [project.run_bot], len(projects), 'Running')
                    futures.append(future)

        with general_buttons_cols[2]:
            if st.button('Train & Run All', use_container_width=True, type='primary'):
                projects = [p for p in app.projects if not p.bot_running]
                for project in projects:
                    future = executor.submit(run_something, [project.train_bot, project.run_bot], len(projects), 'Trained and running')
                    futures.append(future)

        with general_buttons_cols[3]:
            if st.button('Stop All', use_container_width=True, type='primary'):
                projects = [p for p in app.projects if p.bot_running]
                for project in projects:
                    future = executor.submit(run_something, [project.stop_bot], len(projects), 'Stopped')
                    futures.append(future)
        for t in executor._threads:
            add_script_run_ctx(t)
    concurrent.futures.wait(futures)
    with general_buttons_cols[4]:
        if st.button('❌ Delete all', use_container_width=True, type='secondary'):
            project = app.projects[0]
            while project is not None:
                if project.bot_running:
                    project.stop_bot()
                project = app.delete_project(project)
            st.session_state[SELECTED_PROJECT] = None
    if futures:
        end_time = time.time()
        elapsed_time_seconds = end_time - start_time
        elapsed_hours = int(elapsed_time_seconds // 3600)
        elapsed_minutes = int(elapsed_time_seconds // 60)
        remaining_seconds = elapsed_time_seconds % 60
        with general_buttons_cols[5]:
            st.info(f"Elapsed Time: {elapsed_hours}:{elapsed_minutes}:{remaining_seconds:.3f}")

    for i, project in enumerate(app.projects):
        button_cols = st.columns([0.6, 0.1, 0.1, 0.1, 0.1])
        with button_cols[0]:
            st.subheader(f'{i+1}. {project.name}')
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
        with button_cols[4]:
            if st.button(
                    key=f'delete_{i}',
                    label='❌ Delete',
                    use_container_width=True,
                    type='secondary'
            ):
                if project.bot_running:
                    project.stop_bot()
                st.session_state[SELECTED_PROJECT] = app.delete_project(project)  # Return previous project
                st.rerun()


def project_customization_container():
    """Show the Project Customization container."""
    app = get_app()
    project = st.session_state[SELECTED_PROJECT]
    c1, c2, c3 = st.columns([0.45, 0.45, 0.1])
    with c1:
        st.header(f'Project: {project.name}')
    with c2:
        project_selection('admin')
    with c3:
        if st.button(
                key='delete',
                label='❌ Delete',
                use_container_width=True,
                type='secondary'
        ):
            if project.bot_running:
                project.stop_bot()
            st.session_state[SELECTED_PROJECT] = app.delete_project(project)  # Return previous project
            st.rerun()
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
    icons_map = {
        NUMERIC: '123',
        TEXTUAL: 'alphabet',
        DATETIME: 'calendar2-date',
        BOOLEAN: 'file-binary'
    }
    selected_field = sac.tabs(
        [sac.TabsItem(label=field.original_name, icon=icons_map[field.type.t]) for field in project.data_schema.field_schemas],
        align='start', return_index=False, grow=True)
    col1, col2 = st.columns([0.4, 0.4])
    field = project.data_schema.get_field(selected_field)
    with col1:
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

    with col2:
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
