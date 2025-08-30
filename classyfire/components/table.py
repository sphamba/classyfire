import streamlit as st

from .filters import filter_entries, filters_include, filters_exclude
from ..database import columns_table, entries_table, update_database


def get_columns_visibility():
    st.write("#### 📑 Visible columns")

    if "columns_visibility" not in st.session_state:
        st.session_state.columns_visibility = {col["key"]: True for col in columns_table.all()}
    if "columns_visibility_key" not in st.session_state:
        st.session_state.columns_visibility_key = 0

    columns_visibility = st.session_state.columns_visibility

    options = [
        {
            "label": "Full",
            "button_type": "primary",
            "columns": [col["key"] for col in columns_table.all()],
        },
        {
            "label": "Only results",
            "button_type": "secondary",
            "columns": ["reference", "results"],
        },
        {
            "label": "Only highlights",
            "button_type": "secondary",
            "columns": ["reference", "highlights"],
        },
    ]
    st_cols = st.columns(len(options))
    for i, option in enumerate(options):
        if st_cols[i].button(option["label"], type=option["button_type"], use_container_width=True):
            columns_visibility = {col["key"]: col["key"] in option["columns"] for col in columns_table.all()}
            st.session_state.columns_visibility = columns_visibility
            st.session_state.columns_visibility_key += 1

    with st.expander("Show column toggles"):
        st_cols = st.columns(len(columns_table.all()))
        return {
            col["key"]: st_cols[i].toggle(
                col["label"],
                value=columns_visibility[col["key"]],
                key=f"columns_visibility_{i}_{st.session_state.columns_visibility_key}",
            )
            for i, col in enumerate(columns_table.all())
        }


def main():
    columns_visibility = get_columns_visibility()

    entries = entries_table.all()
    filtered_entries = filter_entries(entries)
    st.write(f"Showing {len(filtered_entries)} of {len(entries)} entries.")

    if "table_key" not in st.session_state:
        st.session_state.table_key = 0

    updated_entries = st.data_editor(
        filtered_entries,
        column_config={
            col["key"]: col["label"] if columns_visibility[col["key"]] else None for col in columns_table.all()
        },
        num_rows="dynamic" if len(filters_include) == 0 and len(filters_exclude) == 0 else "fixed",
        key=f"table_{st.session_state.table_key}",
    )

    if len(filters_include) > 0:
        st.info("Clear filters to add or remove entries.")

    def discard_callback():
        st.session_state.table_key += 1

    update_database(filtered_entries, updated_entries, discard_callback=discard_callback)
