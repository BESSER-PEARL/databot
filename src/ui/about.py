from pathlib import Path

import streamlit as st


def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text(encoding='utf-8')


def about():
    readme = read_markdown_file("README.md")
    readme = '#' + readme.replace('![DataBot Playground Screenshot](docs/source/img/playground_screenshot.png)', '')
    st.markdown(readme)
