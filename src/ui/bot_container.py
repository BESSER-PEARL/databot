import json
import threading
from datetime import datetime

import pandas as pd
import streamlit as st
import websocket
from audio_recorder_streamlit import audio_recorder
from besser.bot.core.message import Message
from plotly import io

from streamlit.components.v1 import html
from streamlit_chat import NO_AVATAR, message
from streamlit.runtime.scriptrunner import add_script_run_ctx

from besser.bot.platforms.payload import Payload, PayloadAction, PayloadEncoder

from src.app.app import get_app
from src.utils.session_monitoring import get_streamlit_session
from src.utils.session_state_keys import AUDIO, BOT_DF_DATA, BOT_DF_SQL, BOT_DF_TITLE, DASHBOARD_TAB, \
    DASHBOARD_TAB_SWITCH, DATAFRAME, HISTORY, LAST_VOICE_MESSAGE, PLOTS, PLOTLY, PLOT_INDEX, PROJECTS, QUEUE, \
    SELECTED_PROJECT, SESSION_ID, STR, TABLES, TABLE_INDEX, USER_INPUT, WEBSOCKET, WEBSOCKET_PORT, WEBSOCKET_THREAD
from src.utils.tweaker import st_tweaker
from src.utils.utils import get_page_height

m_count = 0
"""int: Message counter to assign a unique key to each message."""


def m_key():
    """Message counter to assign a unique key to each message."""
    global m_count
    m_count += 1
    return m_count


def websocket_connection():
    """Create a WebSocket connection for a new user session."""
    project = st.session_state[SELECTED_PROJECT]

    def on_message(ws, payload_str):
        # https://github.com/streamlit/streamlit/issues/2838
        streamlit_session = get_streamlit_session()
        payload: Payload = Payload.decode(payload_str)
        if payload.action == PayloadAction.BOT_REPLY_STR.value:
            content = payload.message
            try:
                # First bot message contains the user's session id (bot session, not streamlit session)
                message_dict = json.loads(payload.message)
                if SESSION_ID in message_dict:
                    streamlit_session._session_state[PROJECTS][project.name][SESSION_ID] = message_dict[SESSION_ID]
                    streamlit_session._handle_rerun_script_request()
                    return
            except Exception as e:
                pass
            t = STR
        elif payload.action == PayloadAction.BOT_REPLY_DF.value:
            content = json.loads(payload.message)
            title = content[BOT_DF_TITLE]
            sql = content[BOT_DF_SQL]
            data = content[BOT_DF_DATA]
            content = pd.DataFrame(data)
            t = DATAFRAME
            streamlit_session._session_state[PROJECTS][project.name][TABLES].append((title, content, sql))
            streamlit_session._session_state[PROJECTS][project.name][TABLE_INDEX] = len(streamlit_session._session_state[PROJECTS][project.name][TABLES]) - 1
            if streamlit_session._session_state[DASHBOARD_TAB] != 0:
                streamlit_session._session_state[DASHBOARD_TAB_SWITCH] = not streamlit_session._session_state[DASHBOARD_TAB_SWITCH]
            streamlit_session._session_state[DASHBOARD_TAB] = 0
        elif payload.action == PayloadAction.BOT_REPLY_PLOTLY.value:
            content = io.from_json(payload.message)
            title = content.layout.title.text
            content.update_layout(title='')
            t = PLOTLY
            streamlit_session._session_state[PROJECTS][project.name][PLOTS].append((title, content))
            streamlit_session._session_state[PROJECTS][project.name][PLOT_INDEX] = len(streamlit_session._session_state[PROJECTS][project.name][PLOTS]) - 1
            if streamlit_session._session_state[DASHBOARD_TAB] != 1:
                streamlit_session._session_state[DASHBOARD_TAB_SWITCH] = not streamlit_session._session_state[DASHBOARD_TAB_SWITCH]
            streamlit_session._session_state[DASHBOARD_TAB] = 1
        message = Message(t, content, is_user=False, timestamp=datetime.now())
        streamlit_session._session_state[PROJECTS][project.name][QUEUE].put(message)
        streamlit_session._handle_rerun_script_request()

    ws = websocket.WebSocketApp(f"ws://localhost:{project.properties[WEBSOCKET_PORT]}/",
                                on_message=on_message)
    websocket_thread = threading.Thread(target=ws.run_forever)
    add_script_run_ctx(websocket_thread)
    websocket_thread.start()
    st.session_state[PROJECTS][project.name][WEBSOCKET] = ws
    st.session_state[PROJECTS][project.name][WEBSOCKET_THREAD] = websocket_thread


def check_websocket_connection():
    """Check the WebSocket connection status of the current user session.

    If there is no WebSocket connection established, creates a new one.

    If there is a dead connection, delete it from the session_state.
    """
    project = st.session_state[SELECTED_PROJECT]

    if WEBSOCKET_THREAD in st.session_state[PROJECTS][project.name] and not st.session_state[PROJECTS][project.name][WEBSOCKET_THREAD].is_alive():
        del st.session_state[PROJECTS][project.name][WEBSOCKET_THREAD]
        del st.session_state[PROJECTS][project.name][WEBSOCKET]
    if WEBSOCKET not in st.session_state[PROJECTS][project.name] and WEBSOCKET_THREAD not in st.session_state[PROJECTS][project.name]:
        websocket_connection()


def bot_container():
    """Show the bot container"""
    global m_count
    m_count = 0
    app = get_app()
    project = st.session_state[SELECTED_PROJECT] if SELECTED_PROJECT in st.session_state else None

    def on_input_change():
        user_input = st.session_state[USER_INPUT]
        st.session_state[USER_INPUT] = ''
        message = Message(STR, user_input, is_user=True, timestamp=datetime.now())
        st.session_state[PROJECTS][project.name][HISTORY].append(message)
        if user_input.endswith('?'):
            user_input = user_input[:-1] + ' ?'
        payload = Payload(action=PayloadAction.USER_MESSAGE,
                          message=user_input)
        try:
            ws.send(json.dumps(payload, cls=PayloadEncoder))
        except Exception as e:
            st.write('No connection established')

    chat_box_css = f"""
        #chat_box {{
            box-shadow: rgb(0 0 0 / 12%) 1px 1px 3px 0px, rgb(0 0 0 / 5%) -1px -1px 3px 0px;
            border-radius: 22px;
            height: {get_page_height(250)}px;
            overflow: scroll;
        }}
    """
    chat_box = st_tweaker.columns([1], id='chat_box', css=chat_box_css)
    with chat_box[0]:
        st.write('')
        if not project:
            message(f'👋 Hi! This is where you will be able to chat with an intelligent assistant about data sources. First, you need to create a project with some data. You can do it in the Admin page!', is_user=False, key=f'message_{m_key()}', avatar_style=NO_AVATAR, logo=None)
        elif not project.bot_running:
            message(f'👋 Hi! I am your assistant to explore {project.name}.', is_user=False, key=f'message_{m_key()}', avatar_style=NO_AVATAR, logo=None)
            message(f'I am afraid I cannot help you right now because I have not been trained yet 😢', is_user=False, key=f'message_{m_key()}', avatar_style=NO_AVATAR, logo=None)
        else:
            check_websocket_connection()
            ws = st.session_state[PROJECTS][project.name][WEBSOCKET]

            while not st.session_state[PROJECTS][project.name][QUEUE].empty():
                m = st.session_state[PROJECTS][project.name][QUEUE].get()
                st.session_state[PROJECTS][project.name][HISTORY].append(m)
            for m in st.session_state[PROJECTS][project.name][HISTORY]:
                if m.type == STR:
                    message(m.content, is_user=m.is_user, key=f'message_{m_key()}', avatar_style=NO_AVATAR, logo=None)
                elif m.type == AUDIO:
                    st.audio(m.content, format="audio/wav")
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.text_input(
            label=USER_INPUT,
            label_visibility='collapsed',
            placeholder='Write your question here',
            on_change=on_input_change,
            key=USER_INPUT,
            disabled=not project or not project.bot_running
        )
    with col2:
        if voice_bytes := audio_recorder(text=None, pause_threshold=2, icon_size='2x', neutral_color='#6b6b6b'):
            if (LAST_VOICE_MESSAGE not in st.session_state or st.session_state[LAST_VOICE_MESSAGE] != voice_bytes) \
                    and project and project.bot_running:
                st.session_state[LAST_VOICE_MESSAGE] = voice_bytes
                # Encode the audio bytes to a base64 string
                voice_message = Message(t=AUDIO, content=voice_bytes, is_user=True, timestamp=datetime.now())
                st.session_state[PROJECTS][project.name][HISTORY].append(voice_message)
                transcription = app.speech2text.speech2text(voice_bytes)
                if transcription.endswith('?'):
                    transcription = transcription[:-1] + ' ?'
                payload = Payload(action=PayloadAction.USER_MESSAGE, message=transcription)
                try:
                    ws.send(json.dumps(payload, cls=PayloadEncoder))
                except Exception as e:
                    st.error('Your message could not be sent. The connection is already closed')

    if project and project.name in st.session_state[PROJECTS]:
        # Scroll the chat box to the bottom
        js = f"""
        <script>
            function scroll(dummy_var_to_force_repeat_execution){{
                var objDiv = parent.document.getElementById("chat_box");
                objDiv.scrollTop = objDiv.scrollHeight + 99999;
            }}
            scroll({len(st.session_state[PROJECTS][project.name][HISTORY])})
        </script>
        """
        html(js)
