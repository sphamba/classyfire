import streamlit as st

from .filters import filter_entries, filters, clear_filters
from ..database import columns_table, entries_table, update_database, add_new_entry


def entry_selection(entries):
    filtered_entries = filter_entries(entries, filters)

    st.write("#### 🗂️ Entry selection")
    st.write(f"Showing {len(filtered_entries)} of {len(entries)} entries.")

    if "single_entry_index" not in st.session_state:
        st.session_state.single_entry_index = 0
    if "single_entry_index_key" not in st.session_state:
        st.session_state.single_entry_index_key = 0

    entry_index = st.selectbox(
        "Select an entry",
        range(len(filtered_entries)),
        index=st.session_state.single_entry_index,
        format_func=lambda i: filtered_entries[i]["reference"] or "",
        label_visibility="collapsed",
        key=f"single_entry_index_{st.session_state.single_entry_index_key}",
    )

    st_cols = st.columns([0.2, 0.6, 0.2])

    if st_cols[0].button(
        "Previous",
        use_container_width=True,
        type="secondary",
        disabled=entry_index == 0,
    ):
        st.session_state.single_entry_index = entry_index - 1
        st.session_state.single_entry_index_key += 1
        st.rerun()

    if st_cols[1].button(
        "Add new entry",
        use_container_width=True,
        type="primary",
    ):
        new_entry = add_new_entry()
        try:
            st.session_state.single_entry_index = entries_table.all().index(new_entry)
        except IndexError:
            st.session_state.single_entry_index = len(entries_table.all()) - 1
        st.session_state.single_entry_index_key += 1
        clear_filters()

    if st_cols[2].button(
        "Next",
        use_container_width=True,
        type="secondary",
        disabled=entry_index == len(filtered_entries) - 1,
    ):
        st.session_state.single_entry_index = entry_index + 1
        st.session_state.single_entry_index_key += 1
        st.rerun()

    entry = filtered_entries[entry_index]

    return entry


def get_updated_entry(entry):
    updated_entry = dict(entry)
    needs_validation = False

    if "must_notify_single_saved" in st.session_state:
        st.toast("Changes saved.", icon="ℹ️")
        del st.session_state.must_notify_single_saved

    for col in columns_table.all():
        value = None
        updated_value = None

        if col["type"] == "text":
            value = entry.get(col["key"], "") or ""
            updated_value = st.text_input(
                col["label"],
                value=value,
                key=f"single_{col['key']}_{st.session_state.single_key}",
            )
            if value != updated_value:
                st.session_state.must_notify_single_saved = True

        elif col["type"] == "markdown":
            value = entry.get(col["key"], "") or ""
            updated_value = st.text_area(
                col["label"],
                value=value,
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

    return updated_entry, needs_validation


def main():
    entries = entries_table.all()
    entry = entry_selection(entries)

    if "single_key" not in st.session_state:
        st.session_state.single_key = 0

    st.write("#### 📝 Notes")

    updated_entry, needs_validation = get_updated_entry(entry)

    if needs_validation:
        st.write("---")

    def discard_callback():
        st.session_state.single_key += 1

    update_database([entry], [updated_entry], discard_callback=discard_callback, needs_validation=needs_validation)
