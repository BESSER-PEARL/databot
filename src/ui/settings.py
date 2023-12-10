import streamlit as st

from src.app.app import get_app
from src.ui.utils.session_state_keys import NLP_STT_HF_MODEL, OPENAI_API_KEY, OPENAI_MODEL_NAME


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
        app.properties[OPENAI_MODEL_NAME] = st.text_input(
            label='OpenAI Model Name',
            help='Introduce the name of the OpenAI model to use in the AI features. Available models: https://platform.openai.com/docs/models',
            value=app.properties[OPENAI_MODEL_NAME]
        )
        app.properties[NLP_STT_HF_MODEL] = st.text_input(
            label='Voice recognition model (HuggingFace endpoint)',
            help='Introduce a model ID from HuggingFace',
            value=app.properties[NLP_STT_HF_MODEL],
            # disabled=True
        )
