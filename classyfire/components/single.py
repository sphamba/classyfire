import streamlit as st

from .filters import filter_entries, filters
from ..database import columns_table, entries_table, update_database


def main():
    entries = entries_table.all()
    filtered_entries = filter_entries(entries, filters)

    st.write("#### 🗂️ Entry selection")
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
    for col in columns_table.all():
        if col["type"] == "text":
            updated_entry[col["key"]] = st.text_input(
                col["label"],
                value=entry.get(col["key"], ""),
                key=f"single_{col['key']}_{st.session_state.single_key}",
            )

        elif col["type"] == "markdown":
            updated_entry[col["key"]] = st.text_area(
                col["label"],
                value=entry.get(col["key"], ""),
                height=200,
                key=f"single_{col['key']}_{st.session_state.single_key}",
            )

        elif col["type"] == "tags":
            options = entry.get(col["key"], []) or []
            updated_entry[col["key"]] = st.multiselect(
                col["label"],
                options,
                default=options,
                accept_new_options=True,
                key=f"single_{col['key']}_{st.session_state.single_key}",
            )

    def discard_callback():
        st.session_state.single_key += 1

    update_database([entry], [updated_entry], discard_callback=discard_callback)
