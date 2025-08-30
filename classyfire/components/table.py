import streamlit as st

from .filters import filter_entries, filters_include, filters_exclude
from ..database import columns_table, entries_table, update_database


def get_columns_visibility():
    st.subheader("🏛️ Visible columns")

    if "columns_visibility" not in st.session_state:
        st.session_state.columns_visibility = {col["key"]: True for col in columns_table.all()}
    if "columns_visibility_key" not in st.session_state:
        st.session_state.columns_visibility_key = 0

    columns_visibility = st.session_state.columns_visibility

    options = [
        {
            "label": "All",
            "button_type": "primary",
            "columns": [col["key"] for col in columns_table.all()],
            "row_height": None,
        },
        {
            "label": "Only results",
            "button_type": "secondary",
            "columns": ["reference", "results"],
            "row_height": 100,
        },
        {
            "label": "Only highlights",
            "button_type": "secondary",
            "columns": ["reference", "highlights"],
            "row_height": 100,
        },
    ]
    st_cols = st.columns(len(options))
    for i, option in enumerate(options):
        if st_cols[i].button(option["label"], type=option["button_type"], use_container_width=True):
            columns_visibility = {col["key"]: col["key"] in option["columns"] for col in columns_table.all()}
            st.session_state.columns_visibility = columns_visibility
            st.session_state.columns_visibility_key += 1
            st.session_state.table_row_height = option["row_height"]

    with st.expander("Show column toggles"):
        return {
            col["key"]: st.toggle(
                col["label"],
                value=columns_visibility[col["key"]],
                key=f"columns_visibility_{i}_{st.session_state.columns_visibility_key}",
            )
            for i, col in enumerate(columns_table.all())
        }


def main():
    if "table_key" not in st.session_state:
        st.session_state.table_key = 0
    if "table_row_height" not in st.session_state:
        st.session_state.table_row_height = None

    columns_visibility = get_columns_visibility()

    st.divider()
    st.subheader("📅 Table")

    entries = entries_table.all()
    filtered_entries = filter_entries(entries)
    st.write(f"_Showing {len(filtered_entries)} of {len(entries)} entries._")
    st.caption(
        'To add a new entry, scroll to the bottom of the table, or use the "🔍 Single view" tab. To remove an entry, select its row using the leftmost column and use the trash icon that appears at the top right corner of the table.'
    )

    filtered_entries_with_view = []
    for entry in filtered_entries:
        doc_id = entry.doc_id
        entry = dict(entry)
        entry["view"] = f"?doc_id={doc_id}"
        entry["doc_id"] = doc_id
        filtered_entries_with_view.append(entry)

    column_config = {col["key"]: col["label"] for col in columns_table.all()}
    column_config.update({
        "view": st.column_config.LinkColumn(
            "",
            display_text="View",
            disabled=True,
        ),
    })
    column_order = ["view"] + [col["key"] for col in columns_table.all() if columns_visibility[col["key"]]]

    updated_entries = st.data_editor(
        filtered_entries_with_view,
        column_config=column_config,
        column_order=column_order,
        num_rows="dynamic" if len(filters_include) == 0 and len(filters_exclude) == 0 else "fixed",
        row_height=st.session_state.table_row_height,
        height=500,
        key=f"table_{st.session_state.table_key}",
    )

    for entry in updated_entries:
        if "view" in entry:
            del entry["view"]
        if "doc_id" in entry:
            del entry["doc_id"]

    if len(filters_include) > 0:
        st.info("Clear filters to add or remove entries.")

    def discard_callback():
        st.session_state.table_key += 1

    update_database(filtered_entries, updated_entries, discard_callback=discard_callback)
