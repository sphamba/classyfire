import streamlit as st

from .filters import main as filters_component
from .single import main as single_component
from .sort import main as sort_component
from .table import main as table_component
from ..i18n import t


def main() -> None:
    print_mode = "print" in st.query_params and st.query_params["print"]

    st.set_page_config(
        page_title="ClassyFire",
        page_icon="🔥",
        layout="centered" if print_mode else "wide",
        menu_items={
            "Get help": "https://github.com/sphamba/classyfire/issues",
            "Report a bug": "https://github.com/sphamba/classyfire/issues",
            "About": "Classify research articles",
        },
    )

    if print_mode:
        single_component(print_mode=True)
        return

    st.markdown(
        "<center style='font-size:3em;font-weight:bold;padding-left:0.4em;'>ClassyFire🔥</center>",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        filters_component()
        st.divider()
        sort_component()

    tabs = st.tabs([f"🔍 {t('Single view')}", f"📅 {t('Table view')}"])

    with tabs[0]:
        st.write("")
        single_component()

    with tabs[1]:
        st.write("")
        table_component()
