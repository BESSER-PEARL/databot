import threading
import time
import streamlit as st

from streamlit.runtime import Runtime
from streamlit.runtime.app_session import AppSession
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

from src.utils.session_state_keys import PROJECTS, WEBSOCKET

SESSION_MONITORING_INTERVAL = 3


def get_streamlit_session() -> AppSession or None:
    """Get the current streamlit user session"""
    session_id = get_script_run_ctx().session_id
    runtime: Runtime = Runtime.instance()
    return next((
        s.session
        for s in runtime._session_mgr.list_sessions()
        if s.session.id == session_id
    ), None)


def session_monitoring(interval: int) -> None:
    """Monitor streamlit sessions to delete all inactive sessions in real time.

    Args:
        interval (int): time interval, in seconds, to check the sessions status
    """
    runtime_set = False
    runtime = None
    while True:
        time.sleep(interval)
        if not runtime_set:
            try:
                runtime = Runtime.instance()
                runtime_set = True
            except Exception as e:
                pass
        else:
            for session_info in runtime._session_mgr.list_sessions():
                session = session_info.session
                if not runtime.is_active_session(session.id):
                    if PROJECTS in session.session_state:
                        for project in session.session_state[PROJECTS]:
                            if WEBSOCKET in session.session_state[PROJECTS][project]:
                                try:
                                    session.session_state[PROJECTS][project][WEBSOCKET].close()
                                except Exception as e:
                                    print(e)
                    runtime.close_session(session.id)


@st.cache_resource
def run_thread_session_monitoring():
    session_monitoring_thread = threading.Thread(target=session_monitoring,
                                                 kwargs={'interval': SESSION_MONITORING_INTERVAL})
    add_script_run_ctx(session_monitoring_thread)
    session_monitoring_thread.start()
    return True
