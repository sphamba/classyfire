import streamlit as st

from .filters import main as filters_component
from .single import main as single_component
from .table import main as table_component


def main():
    st.set_page_config(
        page_title="Classy Fire 🔥",
        page_icon="🔥",
        layout="wide",
        menu_items={
            "Get help": "https://github.com/sphamba/classyfire/issues",
            "Report a bug": "https://github.com/sphamba/classyfire/issues",
            "About": "Classify research articles",
        },
    )
    st.write("# _cf.:_ Classy Fire🔥")

    with st.sidebar:
        filters_component()

    st.write("#### 👀 View mode")
    tabs = st.tabs(["🔍 Single view", "📋 Table view"])

    with tabs[0]:
        single_component()

    with tabs[1]:
        table_component()
