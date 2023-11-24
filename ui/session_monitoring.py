import time

from streamlit.runtime import Runtime
from streamlit.runtime.app_session import AppSession
from streamlit.runtime.scriptrunner import get_script_run_ctx


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
                runtime: Runtime = Runtime.instance()
                runtime_set = True
            except Exception as e:
                pass
        else:
            for session_info in runtime._session_mgr.list_sessions():
                session = session_info.session
                if not runtime.is_active_session(session.id):
                    if 'websocket' in session.session_state:
                        session.session_state['websocket'].close()
                    runtime.close_session(session.id)
