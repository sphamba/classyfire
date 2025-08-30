import streamlit as st

from .filters import filter_entries, filters
from ..database import columns_table, entries_table


if "table_key" not in st.session_state:
    st.session_state.table_key = 0


def update_database(original_entries, updated_entries):
    if [dict(entry) for entry in original_entries] == updated_entries:
        return

    cols = st.columns(3)
    with cols[0]:
        st.warning("You have unsaved changes.", icon="⚠️")

    with cols[1]:
        if st.button("Save changes", type="primary", width="stretch"):
            removed_ids = [entry.doc_id for entry in original_entries if entry not in updated_entries]
            entries_table.remove(doc_ids=removed_ids)
            new_entries = [entry for entry in updated_entries if entry not in original_entries]
            entries_table.insert_multiple(new_entries)
            st.rerun()

    with cols[2]:
        if st.button("Discard changes", type="secondary", width="stretch"):
            st.session_state.table_key += 1
            st.rerun()


def main():
    entries = entries_table.all()
    filtered_entries = filter_entries(entries, filters)
    st.write(f"Showing {len(filtered_entries)} of {len(entries)} entries.")

    updated_entries = st.data_editor(
        filtered_entries,
        column_config={ col["key"]: col["label"] for col in columns_table.all() },
        num_rows="dynamic" if len(filters) == 0 else "fixed",
        key=st.session_state.table_key
    )

    if len(filters) > 0:
        st.info("Clear filters to add or remove entries.")

    update_database(filtered_entries, updated_entries)
