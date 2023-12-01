import sys

import streamlit as st
from streamlit.web import cli as stcli

from app.app import create_app
from ui.admin import admin
from ui.playground import playground
from ui.utils.session_monitoring import run_thread_session_monitoring
from ui.settings import settings
from ui.sidebar import sidebar_menu
from ui.utils.utils import disable_input_focusout, remove_header, remove_top_margin, \
    set_screen_data_component

st.set_page_config(layout="wide")

if __name__ == "__main__":
    if st.runtime.exists():
        # Used to get screen info, e.g., the height and width
        set_screen_data_component()
        # Create the app, only 1 time, shared across sessions
        create_app()
        # Run session monitoring in another thread, only 1 time
        run_thread_session_monitoring()
        # Show menu in sidebar
        with st.sidebar:
            page = sidebar_menu()
        # Remove top margin
        remove_top_margin(page)
        # Remove Streamlit's header
        remove_header()
        # Display a page
        if page == 'Playground':
            playground()
        elif page == 'Admin':
            admin()
        elif page == 'Settings':
            settings()

        disable_input_focusout()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
