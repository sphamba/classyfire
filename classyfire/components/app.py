import streamlit as st

from .filters import main as filters_component
from .single import main as single_component
from .table import main as table_component


def main():
    st.set_page_config(
        page_title="ClassyFire",
        page_icon="🔥",
        layout="wide",
        menu_items={
            "Get help": "https://github.com/sphamba/classyfire/issues",
            "Report a bug": "https://github.com/sphamba/classyfire/issues",
            "About": "Classify research articles",
        },
    )
    st.markdown("<center style='font-size:3em;font-weight:bold;'>ClassyFire🔥</center>", unsafe_allow_html=True)

    with st.sidebar:
        filters_component()

    tabs = st.tabs(["🔍 Single view", "📅 Table view"])

    with tabs[0]:
        st.write("")
        single_component()

    with tabs[1]:
        st.write("")
        table_component()
