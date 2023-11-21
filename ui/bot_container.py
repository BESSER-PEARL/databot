import json
import queue
import threading
import pandas as pd
import streamlit as st
import websocket
from besser.bot.platforms.websocket.message import Message
from plotly import io

from streamlit_chat import NO_AVATAR, message
from streamlit.runtime.scriptrunner import add_script_run_ctx

from besser.bot.platforms.payload import Payload, PayloadAction, PayloadEncoder

from app.app import app
from ui.session_monitoring import get_streamlit_session


m_count = 0
"""int: Message counter to assign a unique key to each message."""


def m_key():
    """Message counter to assign a unique key to each message."""
    global m_count
    m_count += 1
    return m_count


def websocket_connection():
    """Create a WebSocket connection for a new user session."""
    def on_message(ws, payload_str):
        # https://github.com/streamlit/streamlit/issues/2838
        streamlit_session = get_streamlit_session()
        payload: Payload = Payload.decode(payload_str)
        if payload.action == PayloadAction.BOT_REPLY_STR.value:
            content = payload.message
            t = 'str'
        elif payload.action == PayloadAction.BOT_REPLY_DF.value:
            content = pd.read_json(payload.message)
            t = 'dataframe'
        elif payload.action == PayloadAction.BOT_REPLY_PLOTLY.value:
            content = io.from_json(payload.message)
            t = 'plotly'
        message = Message(t, content, is_user=False)
        if message.type == 'plotly':
            app.selected_project.plot = message.content
        streamlit_session._session_state['queue'].put(message)
        streamlit_session._handle_rerun_script_request()

    ws = websocket.WebSocketApp("ws://localhost:8765/",
                                on_message=on_message)
    websocket_thread = threading.Thread(target=ws.run_forever)
    add_script_run_ctx(websocket_thread)
    websocket_thread.start()
    st.session_state['websocket'] = ws
    st.session_state['websocket_thread'] = websocket_thread


def check_websocket_connection():
    """Check the WebSocket connection status of the current user session.

    If there is no WebSocket connection established, creates a new one.

    If there is a dead connection, delete it from the session_state.
    """
    if 'websocket_thread' in st.session_state and not st.session_state['websocket_thread'].is_alive():
        del st.session_state['websocket_thread']
        del st.session_state['websocket']
    if 'websocket' not in st.session_state and 'websocket_thread' not in st.session_state:
        print('retrying websocket connection...')
        websocket_connection()


def bot_container():
    """Show the bot container"""
    def on_input_change():
        user_input = st.session_state['user_input']
        st.session_state['user_input'] = ''
        message = Message('str', user_input, is_user=True)
        st.session_state['history'].append(message)
        payload = Payload(action=PayloadAction.USER_MESSAGE,
                          message=user_input)
        try:
            ws.send(json.dumps(payload, cls=PayloadEncoder))
        except:
            st.write('No connection established')

    with st.expander('Show/hide chat', expanded=True):
        # [data-testid="stExpander"] # this condition fails in streamlit 1.28.0, not in 1.27.0: div:has(>.streamlit-expanderContent) {
        css = '''
            <style>
                .streamlit-expanderContent {
                    overflow: scroll;
                    height: 400px;
                }
            }
            </style>
            '''
        st.markdown(css, unsafe_allow_html=True)
        if not app.selected_project:
            message(f'Hi! This is where you will be able to chat with an intelligent assistant about data sources. First, you need to create a project with some data. You can do it in the Admin page!', is_user=False, key=f'message_{m_key()}', avatar_style=NO_AVATAR, logo=None)

        elif not app.selected_project.bot_running:
            message(f'Hi! I am you assistant to explore {app.selected_project.name}.', is_user=False, key=f'message_{m_key()}', avatar_style=NO_AVATAR, logo=None)
            message(f'I am afraid I cannot help you right now because I have not been trained yet 😢', is_user=False, key=f'message_{m_key()}', avatar_style=NO_AVATAR, logo=None)

        else:
            check_websocket_connection()
            ws = st.session_state['websocket']

            if 'history' not in st.session_state:
                st.session_state['history'] = []

            if 'queue' not in st.session_state:
                st.session_state['queue'] = queue.Queue()

            while not st.session_state['queue'].empty():
                m = st.session_state['queue'].get()
                st.session_state['history'].append(m)
            for m in st.session_state['history']:
                if m.type == 'str':
                    message(m.content, is_user=m.is_user, key=f'message_{m_key()}', avatar_style=NO_AVATAR, logo=None)
    st.text_input(
        label='user_input',
        label_visibility='collapsed',
        placeholder='Write your question here',
        on_change=on_input_change,
        key="user_input",
        disabled=not app.selected_project or not app.selected_project.bot_running
    )

