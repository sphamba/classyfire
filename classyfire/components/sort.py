import re

import streamlit as st
from tinydb.table import Document

from ..i18n import t


method = "modified"


def extract_date(entry: Document) -> str:
    reference = entry.get("reference", "")
    result = re.search(r"\b(1|2)\d{3}\b", reference)
    if result:
        return result.group(0)
    return "9999"


def sort_entries(entries: list[Document]) -> list[Document]:
    if method == "modified":
        return sorted(entries, key=lambda e: e.doc_id, reverse=True)
    elif method == "alphabetical":
        return sorted(entries, key=lambda e: e.get("reference", "").lower())
    elif method == "date":
        return sorted(entries, key=lambda e: extract_date(e), reverse=True)
    return entries


def main() -> None:
    global method

    st.header(f"🔀 {t('Sort')}")

    options = {
        t("Last modified"): "modified",
        t("Alphabetical (references)"): "alphabetical",
        t("Publication date"): "date",
    }

    label = st.radio(
        t("Sort by"),
        options,
    )

    method = options[label]
