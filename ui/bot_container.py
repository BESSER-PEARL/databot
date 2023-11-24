import json
import threading
import pandas as pd
import streamlit as st
import websocket
from audio_recorder_streamlit import audio_recorder
from besser.bot.platforms.websocket.message import Message
from plotly import io

from streamlit_chat import NO_AVATAR, message
from streamlit.runtime.scriptrunner import add_script_run_ctx

from besser.bot.platforms.payload import Payload, PayloadAction, PayloadEncoder

from app.app import app
from ui.session_monitoring import get_streamlit_session
from ui.utils.tweaker import st_tweaker
from streamlit.components.v1 import html

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
            streamlit_session._session_state[app.selected_project.name]['plot'] = message.content
        streamlit_session._session_state[app.selected_project.name]['queue'].put(message)
        streamlit_session._handle_rerun_script_request()

    ws = websocket.WebSocketApp(f"ws://localhost:{app.selected_project.properties['websocket.port']}/",
                                on_message=on_message)
    websocket_thread = threading.Thread(target=ws.run_forever)
    add_script_run_ctx(websocket_thread)
    websocket_thread.start()
    st.session_state[app.selected_project.name]['websocket'] = ws
    st.session_state[app.selected_project.name]['websocket_thread'] = websocket_thread


def check_websocket_connection():
    """Check the WebSocket connection status of the current user session.

    If there is no WebSocket connection established, creates a new one.

    If there is a dead connection, delete it from the session_state.
    """
    if 'websocket_thread' in st.session_state[app.selected_project.name] and not st.session_state[app.selected_project.name]['websocket_thread'].is_alive():
        del st.session_state[app.selected_project.name]['websocket_thread']
        del st.session_state[app.selected_project.name]['websocket']
    if 'websocket' not in st.session_state[app.selected_project.name] and 'websocket_thread' not in st.session_state[app.selected_project.name]:
        print('retrying websocket connection...')
        websocket_connection()


def bot_container():
    """Show the bot container"""
    global m_count
    m_count = 0

    def on_input_change():
        user_input = st.session_state['user_input']
        st.session_state['user_input'] = ''
        message = Message('str', user_input, is_user=True)
        st.session_state[app.selected_project.name]['history'].append(message)
        payload = Payload(action=PayloadAction.USER_MESSAGE,
                          message=user_input)
        try:
            ws.send(json.dumps(payload, cls=PayloadEncoder))
        except:
            st.write('No connection established')

    chat_box_css = """
        #chat_box {
            box-shadow: rgb(0 0 0 / 20%) 0px 2px 1px -1px, rgb(0 0 0 / 14%) 0px 1px 1px 0px, rgb(0 0 0 / 12%) 0px 1px 3px 0px;
            border-radius: 15px;
            color: red;
            overflow: scroll;
            height: 400px;
        }
    """
    chat_box = st_tweaker.columns([1], id='chat_box', css=chat_box_css)
    with chat_box[0]:
        st.write('')
        if not app.selected_project:
            message(f'Hi! This is where you will be able to chat with an intelligent assistant about data sources. First, you need to create a project with some data. You can do it in the Admin page!', is_user=False, key=f'message_{m_key()}', avatar_style=NO_AVATAR, logo=None)

        elif not app.selected_project.bot_running:
            message(f'Hi! I am your assistant to explore {app.selected_project.name}.', is_user=False, key=f'message_{m_key()}', avatar_style=NO_AVATAR, logo=None)
            message(f'I am afraid I cannot help you right now because I have not been trained yet 😢', is_user=False, key=f'message_{m_key()}', avatar_style=NO_AVATAR, logo=None)

        else:
            check_websocket_connection()
            ws = st.session_state[app.selected_project.name]['websocket']

            while not st.session_state[app.selected_project.name]['queue'].empty():
                m = st.session_state[app.selected_project.name]['queue'].get()
                st.session_state[app.selected_project.name]['history'].append(m)
            for m in st.session_state[app.selected_project.name]['history']:
                if m.type == 'str':
                    message(m.content, is_user=m.is_user, key=f'message_{m_key()}', avatar_style=NO_AVATAR, logo=None)
                elif m.type == 'audio':
                    st.audio(m.content, format="audio/wav")
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.text_input(
            label='user_input',
            label_visibility='collapsed',
            placeholder='Write your question here',
            on_change=on_input_change,
            key="user_input",
            disabled=not app.selected_project or not app.selected_project.bot_running
        )
    with col2:
        if voice_bytes := audio_recorder(text=None, pause_threshold=2, icon_size='2x', neutral_color='#6b6b6b'):
            if ('last_voice_message' not in st.session_state or st.session_state['last_voice_message'] != voice_bytes) \
                    and app.selected_project and app.selected_project.bot_running:
                st.session_state['last_voice_message'] = voice_bytes
                # Encode the audio bytes to a base64 string
                voice_message = Message(t='audio', content=voice_bytes, is_user=True)
                st.session_state[app.selected_project.name]['history'].append(voice_message)
                transcription = app.speech2text.speech2text(voice_bytes)
                payload = Payload(action=PayloadAction.USER_MESSAGE, message=transcription)
                try:
                    ws.send(json.dumps(payload, cls=PayloadEncoder))
                except Exception as e:
                    st.error('Your message could not be sent. The connection is already closed')

    if app.selected_project and app.selected_project.name in st.session_state:
        # Scroll the chat box to the bottom
        js = f"""
        <script>
            function scroll(dummy_var_to_force_repeat_execution){{
                var objDiv = parent.document.getElementById("chat_box");
                objDiv.scrollTop = objDiv.scrollHeight + 99999;
            }}
            scroll({len(st.session_state[app.selected_project.name]['history'])})
        </script>
        """
        st.components.v1.html(js)
