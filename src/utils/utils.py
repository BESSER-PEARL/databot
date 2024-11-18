import streamlit as st
from st_screen_stats import ScreenData
from streamlit.components.v1 import html

from src.app.app import get_app
from src.utils.session_state_keys import SCREEN_DATA, SELECTED_PROJECT


def project_selection(page):
    """Show a project selection container"""
    app = get_app()
    project = st.session_state[SELECTED_PROJECT] if SELECTED_PROJECT in st.session_state else None

    def update_selected_project():
        st.session_state[SELECTED_PROJECT] = app.get_project(st.session_state[f'select_project_selectbox_{page}'])

    if page == 'admin':
        help_message = 'Select the project you want to manage'
    elif page == 'playground':
        help_message = 'Select a project to start chatting with its bot'
    selected_project = st.selectbox(
        label='Select a project',
        options=[project.name for project in app.projects],
        index=app.projects.index(project) if project else 0,
        key=f'select_project_selectbox_{page}',
        on_change=update_selected_project,
        label_visibility='collapsed',
        help=help_message
    )
    st.session_state[SELECTED_PROJECT] = app.get_project(selected_project)


def clear_box(key: str):
    """
    Clears an input box after introducing a value. This is necessary because Streamlit does not clear input boxes after
    introducing a value.

    Args:
        key (str): the key of the streamlit session_state variable containing the input value
    """
    st.session_state[f'{key}_input'] = st.session_state[key]
    st.session_state[key] = ''


def get_input_value(key):
    """
    Gets the value of an input box. This is necessary because Streamlit does not clear input boxes after introducing a
    value. We do it using the clear_box function, storing the value in a temporary variable, and getting it with this
    function.

    Args:
        key (str): the key of the streamlit session_state variable containing the input value
    """
    if f'{key}_input' in st.session_state:
        input_value = st.session_state[f'{key}_input']
        st.session_state[f'{key}_input'] = None
        return input_value
    return None


def set_screen_data_component():
    """Used to get screen info, e.g., the height and width."""
    screen_data = ScreenData(setTimeout=100)
    screen_data.st_screen_data_window_top(key=SCREEN_DATA)


def get_page_height(subtract: int):
    """Get the page height, subtracting a specific amount of pixels. If not set yet, return a default value of 500."""
    try:
        return st.session_state[SCREEN_DATA]['innerHeight'] - subtract
    except Exception as e:
        return 500


def disable_input_focusout():
    """Add a script to the UI html code to avoid introducing a value in a text input box when it is focused out, so it
    is only introduced when the enter key is pressed."""
    html(
        """
        <script>
        const doc = window.parent.document;
        const inputs = doc.querySelectorAll('input');
    
        inputs.forEach(input => {
            input.addEventListener('focusout', function(event) {
                event.stopPropagation();
                event.preventDefault();
            });
        });
        </script>
        """,
        height=0,
        width=0,
        )


def remove_top_margin(page: str):
    """Remove the top margin of a page"""
    page_margins = {
        'Playground': -140,
        'Admin': -100,
        'Settings': -120,
        'About DataBot': -120
    }
    st.html(
        f"""
            <style>
                .stAppViewContainer .stMain .stMainBlockContainer {{
                    margin-top: {page_margins[page]}px;
                }}
            </style>"""
    )


def remove_header():
    """Remove Streamlit's header (and footer)"""
    st.markdown(
        """
            <style>
                header {
                    visibility: hidden;
                    height: 0%;
                }
                footer {
                    visibility: hidden;
                    height: 0%;
                }
            </style>
            """,
        unsafe_allow_html=True
    )


def toggle_button(*args, key=None, initial_value=False, **kwargs):
    if key is None:
        raise ValueError("Must pass key")

    if key not in st.session_state:
        st.session_state[key] = initial_value

    if "type" not in kwargs:
        kwargs["type"] = "primary" if st.session_state[key] else "secondary"

    if st.button(*args, **kwargs):
        st.session_state[key] = not st.session_state[key]
        st.rerun()
