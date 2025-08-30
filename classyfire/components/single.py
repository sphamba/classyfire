import streamlit as st

from .filters import filter_entries, filters
from ..database import columns_table, entries_table, update_database


def main():
    entries = entries_table.all()
    filtered_entries = filter_entries(entries, filters)

    st.write("#### 🗂️ Entry selection")
    st.write(f"Showing {len(filtered_entries)} of {len(entries)} entries.")
    entry_index = st.selectbox(
        "Select an entry",
        range(len(filtered_entries)),
        format_func=lambda i: filtered_entries[i]["reference"],
        label_visibility="collapsed",
    )
    entry = filtered_entries[entry_index]
    updated_entry = dict(entry)

    if "single_key" not in st.session_state:
        st.session_state.single_key = 0

    st.write("#### 📝 Notes")
    needs_validation = False

    if "must_notify_single_saved" in st.session_state:
        st.toast("Changes saved.", icon="ℹ️")
        del st.session_state.must_notify_single_saved

    for col in columns_table.all():
        value = None
        updated_value = None

        if col["type"] == "text":
            value = entry.get(col["key"], "")
            updated_value = st.text_input(
                col["label"],
                value=value,
                key=f"single_{col['key']}_{st.session_state.single_key}",
            )
            if value != updated_value:
                st.session_state.must_notify_single_saved = True

        elif col["type"] == "markdown":
            value = entry.get(col["key"], "")
            updated_value = st.text_area(
                col["label"],
                value=entry.get(col["key"], ""),
                height=200,
                key=f"single_{col['key']}_{st.session_state.single_key}",
            )
            if value != updated_value:
                st.session_state.must_notify_single_saved = True

        elif col["type"] == "tags":
            value = entry.get(col["key"], []) or []
            updated_value = st.multiselect(
                col["label"],
                value,
                default=value,
                accept_new_options=True,
                key=f"single_{col['key']}_{st.session_state.single_key}",
            )
            if value != updated_value:
                st.info("Unsaved changes. Scroll down to validate or undo.", icon="ℹ️")
                needs_validation = True

        updated_entry[col["key"]] = updated_value

    st.write("---")

    def discard_callback():
        st.session_state.single_key += 1

    update_database([entry], [updated_entry], discard_callback=discard_callback, needs_validation=needs_validation)
