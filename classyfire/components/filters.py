import streamlit as st
from tinydb.table import Document

from ..database import columns_table, get_filters_options
from ..i18n import t


filters_include: list[str] = []
filters_exclude: list[str] = []


def filter_entries(entries: list[Document]) -> list[Document]:
    for filter in filters_include:
        if "|" in filter:
            key, value = filter.split("|", 1)
            if key in [col["key"] for col in columns_table.all()]:
                entries = [
                    entry
                    for entry in entries
                    if value.lower() in [tag.lower().split(":")[0] for tag in entry.get(key, []) or []]
                ]
                continue

        entries = [entry for entry in entries if any(filter.lower() in str(v).lower() for v in entry.values())]

    for filters in filters_exclude:
        if "|" in filters:
            key, value = filters.split("|", 1)
            if key in [col["key"] for col in columns_table.all()]:
                entries = [
                    entry
                    for entry in entries
                    if value.lower() not in [tag.lower().split(":")[0] for tag in entry.get(key, []) or []]
                ]
                continue

        entries = [entry for entry in entries if all(filters.lower() not in str(v).lower() for v in entry.values())]

    return entries


def clear_filters() -> None:
    filters_include.clear()
    st.session_state.filters_key += 1
    st.rerun()


def main() -> None:
    if "filters_key" not in st.session_state:
        st.session_state.filters_key = 0

    st.header(f"🧩 {t('Filters')}")
    st.caption(t("filters_caption"))

    filters_options = get_filters_options()

    filters_include[:] = st.multiselect(
        t("Include"),
        filters_options,
        placeholder=t("Add filters"),
        accept_new_options=True,
        key=f"filters_include_{st.session_state.filters_key}",
    )

    filters_exclude[:] = st.multiselect(
        t("Exclude"),
        filters_options,
        placeholder=t("Add filters"),
        accept_new_options=True,
        key=f"filters_exclude_{st.session_state.filters_key}",
    )

    for filter in filters_include + filters_exclude:
        if ":" in filter:
            key, _ = filter.split(":", 1)
            if key not in [col["key"] for col in columns_table.all()]:
                st.warning(f'{t("invalid_tag_type_1")}"`{key}:`"{t("invalid_tag_type_2")}')

    if st.button(t("Clear filters"), type="secondary", use_container_width=True):
        clear_filters()
