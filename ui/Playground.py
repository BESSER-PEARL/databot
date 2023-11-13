import sys

import numpy as np
import pandas as pd
import streamlit as st
from streamlit.runtime import Runtime
from streamlit.web import cli as stcli

from ui.bot_container import bot_container
from ui.sidebar import project_selection
from app.app import app


BOT_CONTAINER_WIDTH = 0.3


def playground():
    """Show the playground container"""
    st.set_page_config(layout="wide")
    with st.sidebar:
        project_selection()
    st.title('📊 BESSER Conversational Data Analysis')
    st.subheader("🤖 Chat assistance")

    bot_col, dash_col = st.columns([BOT_CONTAINER_WIDTH, 1 - BOT_CONTAINER_WIDTH])
    with bot_col:
        bot_container()

    with dash_col:
        # Sample DataFrame
        data = {'col1': [10, 20, 5, 3, 4],
                'col2': [1, 1, 1, 1, 1]}
        df = pd.DataFrame(data)

        chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
        col1, col2 = st.columns(2)

        with col1:
            st.line_chart(chart_data)

        with col2:
            st.bar_chart(df)


if __name__ == "__main__":

    if st.runtime.exists():
        playground()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
