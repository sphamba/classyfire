import streamlit as st

from .filters import filter_entries, clear_filters
from ..database import columns_table, entries_table, update_database, add_new_entry, delete_entry


def create_new_entry():
    new_entry = add_new_entry()
    st.session_state.single_entry_doc_index = new_entry.doc_id
    st.session_state.single_entry_index_key += 1
    st.session_state.single_key += 1
    clear_filters()


def entry_selection(entries):
    filtered_entries = filter_entries(entries)

    st.subheader("👉 Entry selection")

    if len(filtered_entries) == 0:
        st.info("No entries match the current filters.", icon="ℹ️")
        if st.button("Add new entry", type="primary", use_container_width=True):
            create_new_entry()
        return None

    st.write(f"_Listing {len(filtered_entries)} of {len(entries)} entries._")

    if "single_entry_doc_index" not in st.session_state:
        if "doc_id" in st.query_params:
            st.session_state.single_entry_doc_index = int(st.query_params["doc_id"][0])
        else:
            st.session_state.single_entry_doc_index = filtered_entries[0].doc_id
    if "single_entry_index_key" not in st.session_state:
        st.session_state.single_entry_index_key = 0

    try:
        entry_index = [entry.doc_id for entry in filtered_entries].index(st.session_state.single_entry_doc_index)
    except ValueError:
        entry_index = 0
        st.session_state.single_entry_doc_index = filtered_entries[entry_index].doc_id

    st_cols = st.columns([0.8, 0.2])

    entry_index = st_cols[0].selectbox(
        "Select an entry",
        range(len(filtered_entries)),
        index=entry_index,
        format_func=lambda i: filtered_entries[i]["reference"] or "",
        label_visibility="collapsed",
        key=f"single_entry_index_{st.session_state.single_entry_index_key}",
    )

    @st.dialog("⚠️ Confirm entry deletion")
    def confirm_delete():
        st.write("Are you sure you want to delete this entry? This action cannot be undone.")
        st.write(f"Reference: {filtered_entries[entry_index].get('reference', '_not set_') or '_not set_'}")
        st_cols = st.columns(2)
        if st_cols[0].button("Delete", type="primary", use_container_width=True):
            delete_entry(filtered_entries[entry_index])
        if st_cols[1].button("Cancel", type="secondary", use_container_width=True):
            st.rerun()

    if st_cols[1].button("Delete entry", type="tertiary", use_container_width=True):
        confirm_delete()

    st_cols = st.columns([0.2, 0.6, 0.2])

    if st_cols[0].button(
        "Previous",
        use_container_width=True,
        type="secondary",
        disabled=entry_index == 0,
    ):
        st.session_state.single_entry_doc_index = filtered_entries[entry_index - 1].doc_id
        st.session_state.single_entry_index_key += 1
        st.session_state.single_key += 1
        st.rerun()

    if st_cols[1].button(
        "Add new entry",
        use_container_width=True,
        type="primary",
    ):
        create_new_entry()

    if st_cols[2].button(
        "Next",
        use_container_width=True,
        type="secondary",
        disabled=entry_index == len(filtered_entries) - 1,
    ):
        st.session_state.single_entry_doc_index = filtered_entries[entry_index + 1].doc_id
        st.session_state.single_entry_index_key += 1
        st.session_state.single_key += 1
        st.rerun()

    if entry_index is None or entry_index < 0 or entry_index >= len(filtered_entries):
        return None
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
                placeholder="Type here",
                key=f"single_{col['key']}_{st.session_state.single_key}",
            )
            if value != updated_value:
                st.session_state.must_notify_single_saved = True

        elif col["type"] == "markdown":
            st.write(f"#### {col['label']}")
            value = entry.get(col["key"], "") or ""
            updated_value = value

            editing_key = f"editing_{col['key']}_{st.session_state.single_key}"
            if editing_key not in st.session_state:
                st.session_state[editing_key] = None

            if st.session_state[editing_key] is not None:
                temporary_value = st.text_area(
                    "",
                    value=st.session_state[editing_key],
                    height=300,
                    placeholder="Type Markdown here",
                    label_visibility="collapsed",
                    key=f"single_{col['key']}_{st.session_state.single_key}",
                )

                st_cols = st.columns(2)
                if st_cols[0].button(
                    "Save",
                    type="primary",
                    key=f"single_save_{col['key']}_{st.session_state.single_key}",
                    use_container_width=True,
                ):
                    updated_value = temporary_value
                    st.session_state[editing_key] = None
                    if value != updated_value:
                        st.session_state.must_notify_single_saved = True
                    else:
                        st.rerun()

                if st_cols[1].button(
                    "Cancel",
                    type="secondary",
                    key=f"single_cancel_{col['key']}_{st.session_state.single_key}",
                    use_container_width=True,
                ):
                    st.session_state[editing_key] = None
                    st.rerun()

            else:
                if value:
                    st.markdown(value)
                else:
                    st.caption("_No content._")

                if st.button("Edit content", type="secondary", key=f"edit_{col['key']}_{st.session_state.single_key}"):
                    st.session_state[editing_key] = value
                    st.rerun()

        elif col["type"] == "tags":
            value = entry.get(col["key"], []) or []

            options = set(value)
            for _entry in entries_table.all():
                options = options.union(_entry.get(col["key"], []) or [])

            updated_value = st.multiselect(
                col["label"],
                sorted(options),
                default=value,
                accept_new_options=True,
                placeholder="Add tags",
                key=f"single_{col['key']}_{st.session_state.single_key}",
            )
            if value != updated_value:
                st.info("Unsaved changes. Scroll down to validate or undo.", icon="ℹ️")
                needs_validation = True

        updated_entry[col["key"]] = updated_value

    return updated_entry, needs_validation


def main():
    if "single_key" not in st.session_state:
        st.session_state.single_key = 0

    entries = entries_table.all()
    entry = entry_selection(entries)

    st.divider()

    if entry is None:
        st.info("No entry selected.", icon="ℹ️")
        return

    st.subheader("📝 Notes")

    updated_entry, needs_validation = get_updated_entry(entry)

    if needs_validation:
        st.divider()

    def discard_callback():
        st.session_state.single_key += 1

    update_database([entry], [updated_entry], discard_callback=discard_callback, needs_validation=needs_validation)
