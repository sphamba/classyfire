import streamlit as st
from tinydb.table import Document

from .filters import filter_entries, clear_filters
from .sort import sort_entries
from ..database import columns_table, entries_table, update_database, add_new_entry, delete_entry
from ..i18n import t


def create_new_entry() -> None:
    new_entry = add_new_entry()
    st.session_state.single_entry_doc_index = new_entry.doc_id
    st.session_state.single_entry_index_key += 1
    st.session_state.single_key += 1
    clear_filters()


def entry_selection(entries: list[Document]) -> Document | None:
    filtered_entries = sort_entries(filter_entries(entries))

    st.subheader(f"👉 {t('Entry selection')}")

    if len(filtered_entries) == 0:
        st.info(t("no_entries_match_info"), icon="ℹ️")
        if st.button(t("Add new entry"), type="primary", use_container_width=True):
            create_new_entry()
        return None

    st.write(f"_{t('Listing')} {len(filtered_entries)} {t('of')} {len(entries)} {t('entries')}._")

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
        t("Select an entry"),
        range(len(filtered_entries)),
        index=entry_index,
        format_func=lambda i: filtered_entries[i]["reference"] or "",
        label_visibility="collapsed",
        key=f"single_entry_index_{st.session_state.single_entry_index_key}",
    )

    @st.dialog(f"⚠️ {t('Confirm entry deletion')}")
    def confirm_delete() -> None:
        st.write(t("delete_entry_confirmation"))
        st.write(
            f"{t('Reference')}: {filtered_entries[entry_index].get('reference', f'_{t("not set")}_') or f'_{t("not set")}_'}"
        )
        st_cols = st.columns(2)
        if st_cols[0].button(t("Delete"), type="primary", use_container_width=True):
            delete_entry(filtered_entries[entry_index])
        if st_cols[1].button(t("Cancel"), type="secondary", use_container_width=True):
            st.rerun()

    if st_cols[1].button(t("Delete entry"), type="tertiary", use_container_width=True):
        confirm_delete()

    st_cols = st.columns([0.2, 0.6, 0.2])

    if st_cols[0].button(
        t("Previous"),
        use_container_width=True,
        type="secondary",
        disabled=entry_index == 0,
    ):
        st.session_state.single_entry_doc_index = filtered_entries[entry_index - 1].doc_id
        st.session_state.single_entry_index_key += 1
        st.session_state.single_key += 1
        st.rerun()

    if st_cols[1].button(
        t("Add new entry"),
        use_container_width=True,
        type="primary",
    ):
        create_new_entry()

    if st_cols[2].button(
        t("Next"),
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


def get_entry_with_updated_text(entry: dict, col: dict) -> dict:
    if col["type"] == "tags":
        return entry

    updated_entry = entry.copy()
    value = ""
    updated_value = ""

    if col["type"] == "text":
        value = entry.get(col["key"], "") or ""
        updated_value = st.text_input(
            col["label"],
            value=value,
            placeholder=t("Type here"),
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
                placeholder=t("Type Markdown here"),
                label_visibility="collapsed",
                key=f"single_{col['key']}_{st.session_state.single_key}",
            )

            st_cols = st.columns(2)
            if st_cols[0].button(
                t("Save"),
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
                t("Cancel"),
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
                st.caption(f"_{t('No content.')}_")

            if st.button(t("Edit content"), type="secondary", key=f"edit_{col['key']}_{st.session_state.single_key}"):
                st.session_state[editing_key] = value
                st.rerun()

    updated_entry[col["key"]] = updated_value
    return updated_entry


def get_entry_with_updated_tags(entry: dict, col: dict) -> tuple[dict, bool]:
    if col["type"] != "tags":
        return entry, False

    updated_entry = entry.copy()
    needs_validation = False
    value = entry.get(col["key"], []) or []

    options = set(value)
    for _entry in entries_table.all():
        options = options.union([tag.split(":")[0] for tag in (_entry.get(col["key"], []) or [])])

    for tag in value:
        if ":" in tag:
            options.remove(tag.split(":")[0])

    updated_value = st.multiselect(
        col["label"],
        sorted(options),
        default=value,
        accept_new_options=True,
        placeholder=t("Add tags"),
        key=f"single_{col['key']}_{st.session_state.single_key}",
    )
    if value != updated_value:
        needs_validation = True

    updated_entry[col["key"]] = updated_value
    return updated_entry, needs_validation


def get_updated_entry(entry: Document) -> tuple[dict, bool]:
    updated_entry = dict(entry)
    needs_validation = False

    if "must_notify_single_saved" in st.session_state:
        st.toast(t("Changes saved."), icon="ℹ️")
        del st.session_state.must_notify_single_saved

    for col in columns_table.all():
        updated_entry = get_entry_with_updated_text(updated_entry, col)

    st.write(f"#### 🏷️ {t('Tags')}")
    st.caption(t("tag_format_caption"))

    for col in columns_table.all():
        updated_entry, col_needs_validation = get_entry_with_updated_tags(updated_entry, col)
        needs_validation = needs_validation or col_needs_validation

    if needs_validation:
        st.info(t("unsaved_changes_info"), icon="ℹ️")

    return updated_entry, needs_validation


def main() -> None:
    if "single_key" not in st.session_state:
        st.session_state.single_key = 0

    entries = entries_table.all()
    entry = entry_selection(entries)

    st.divider()

    if entry is None:
        st.info(t("No entry selected."), icon="ℹ️")
        return

    st.subheader(f"📝 {t('Notes')}")

    updated_entry, needs_validation = get_updated_entry(entry)

    st.divider()

    def discard_callback() -> None:
        st.session_state.single_key += 1

    update_database([entry], [updated_entry], discard_callback=discard_callback, needs_validation=needs_validation)
