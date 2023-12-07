import streamlit as st

from app.app import get_app
from ui.utils.session_state_keys import NLP_STT_HF_MODEL, OPENAI_API_KEY


def settings():
    app = get_app()

    col1, col2 = st.columns([0.5, 0.5])
    with col1:
        st.header('Settings')
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
            # disabled=True
        )
