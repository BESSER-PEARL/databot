from pathlib import Path

import streamlit as st


def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text(encoding='utf-8')


def about():
    intro_markdown = read_markdown_file("README.md")
    st.markdown('#' + intro_markdown)
