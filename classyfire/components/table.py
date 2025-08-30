import streamlit as st

from .filters import filter_entries, filters
from ..database import columns_table, entries_table


def main():
    entries = entries_table.all()
    filtered_entries = filter_entries(entries, filters)
    st.write(f"Showing {len(filtered_entries)} of {len(entries)} entries.")
    if "table_key" not in st.session_state:
        st.session_state.table_key = 0
    updated_entries = st.data_editor(
        filtered_entries,
        column_config={ col["key"]: col["label"] for col in columns_table.all() },
        num_rows="dynamic" if len(filters) == 0 else "fixed",
        key=st.session_state.table_key
    )

    if len(filters) > 0:
        st.info("Clear filters to add or remove entries.")

    if [dict(entry) for entry in filtered_entries] != updated_entries:
        if st.button("Save changes", type="primary"):
            entries_table.remove(doc_ids=[entry.doc_id for entry in filtered_entries])
            entries_table.insert_multiple(updated_entries)
            st.rerun()

        if st.button("Discard changes", type="secondary"):
            st.session_state.table_key += 1
            st.rerun()
