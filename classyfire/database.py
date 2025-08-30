from typing import Callable

import streamlit as st
from tinydb import TinyDB
from tinydb.table import Document

from .config import DB_PATH
from .i18n import t


def init_columns() -> None:
    if len(columns_table.all()) == 0:
        columns_table.insert_multiple([
            {
                "key": "reference",
                "label": t("Reference"),
                "type": "text",
            },
            {
                "key": "theme",
                "label": t("Theme"),
                "type": "markdown",
            },
            {
                "key": "results",
                "label": t("Results"),
                "type": "markdown",
            },
            {
                "key": "highlights",
                "label": t("Highlights"),
                "type": "markdown",
            },
            {
                "key": "criticisms",
                "label": t("Criticisms"),
                "type": "markdown",
            },
            {
                "key": "authors",
                "label": t("Authors"),
                "type": "tags",
            },
            {
                "key": "definitions",
                "label": t("Definitions"),
                "type": "tags",
            },
            {
                "key": "concepts",
                "label": t("Concepts"),
                "type": "tags",
            },
            {
                "key": "tools",
                "label": t("Tools"),
                "type": "tags",
            },
        ])


def init_entries() -> None:
    if len(entries_table.all()) == 0:
        entries_table.insert_multiple([
            {
                "reference": "Doe et al. (2023)",
                "theme": "Sample Theme",
                "results": "Sample results in **markdown**.",
                "highlights": "Sample highlights in **markdown**.",
                "criticisms": "Sample criticisms in **markdown**.",
                "authors": ["John Doe", "Jane Smith"],
                "definitions": ["definition1", "definition2"],
                "concepts": ["concept1", "concept2"],
                "tools": ["tool1", "tool2"],
            },
            {
                "reference": "Johnson et al. (2024)",
                "theme": "Another Theme",
                "results": "Another set of results in **markdown**.",
                "highlights": "Another set of highlights in **markdown**.",
                "criticisms": "Another set of criticisms in **markdown**.",
                "authors": ["Alice Johnson", "Bob Brown"],
                "definitions": ["definition3", "definition4"],
                "concepts": ["concept3", "concept4"],
                "tools": ["tool3", "tool4"],
            },
        ])


def get_filters_options() -> list[str]:
    options = set()

    for col in columns_table.all():
        if not col["type"] == "tags":
            continue

        for entry in entries_table.all():
            tags = entry.get(col["key"], []) or []
            tags = [tag.lower() for tag in tags]
            prefixed_tags = [f"{col['key']}:{tag}" for tag in tags]
            options.update(tags)
            options.update(prefixed_tags)

    return sorted(options)


def update_database(
    original_entries: list[Document],
    updated_entries: list[dict],
    discard_callback: Callable | None = None,
    needs_validation: bool = True,
) -> None:
    if [dict(entry) for entry in original_entries] == updated_entries:
        return

    st_cols = st.columns(3, vertical_alignment="center")

    with st_cols[0]:
        st.warning("You have unsaved changes.", icon="⚠️")

    with st_cols[1]:
        if st.button("Save changes", type="primary", width="stretch") or not needs_validation:
            if len(original_entries) == 1 and len(updated_entries) == 1:
                entries_table.update(updated_entries[0], doc_ids=[original_entries[0].doc_id])
                st.rerun()

            removed_ids = [entry.doc_id for entry in original_entries if entry not in updated_entries]
            new_entries = [entry for entry in updated_entries if entry not in original_entries]

            if len(removed_ids) == 1 and len(new_entries) == 1:
                entries_table.update(new_entries[0], doc_ids=[removed_ids[0]])
                st.rerun()

            entries_table.remove(doc_ids=removed_ids)
            entries_table.insert_multiple(new_entries)
            st.rerun()

    with st_cols[2]:
        if st.button("Discard changes", type="secondary", width="stretch"):
            if discard_callback:
                discard_callback()
            st.rerun()


def add_new_entry() -> Document:
    new_entry = {col["key"]: None for col in columns_table.all()}
    id = entries_table.insert(new_entry)
    return entries_table.get(doc_id=id)


def delete_entry(entry: Document) -> None:
    entries_table.remove(doc_ids=[entry.doc_id])
    st.rerun()


db = TinyDB(DB_PATH)
columns_table = db.table("columns")
entries_table = db.table("entries")
init_columns()
init_entries()
