import streamlit as st
from tinydb.table import Document

from ..i18n import t


method = "modified"


def sort_entries(entries: list[Document]) -> list[Document]:
    if method == "modified":
        return sorted(entries, key=lambda e: e.doc_id, reverse=True)
    elif method == "alphabetical":
        return sorted(entries, key=lambda e: e.get("reference", "").lower())
    return entries


def main() -> None:
    global method

    st.header(f"🔀 {t('Sort')}")

    options = {
        t("Last modified"): "modified",
        t("Alphabetical (references)"): "alphabetical",
    }

    label = st.radio(
        t("Sort by"),
        options,
    )

    method = options[label]
