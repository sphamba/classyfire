import streamlit as st

from ..database import columns_table, filters_options


filters = []


def filter_entries(entries, filters):
    for filter in filters:
        if ":" in filter:
            key, value = filter.split(":", 1)
            if key in [col["key"] for col in columns_table.all()]:
                entries = [entry for entry in entries if value.lower() in [tag.lower() for tag in entry.get(key, []) or []]]
                continue

        entries = [entry for entry in entries if any(filter.lower() in str(v).lower() for v in entry.values())]

    return entries


def main():
    filters[:] = st.multiselect(
        "Filters",
        filters_options,
        placeholder="Filter by text or tags",
        accept_new_options=True,
    )

    for filter in filters:
        if ":" in filter:
            key, _ = filter.split(":", 1)
            if key not in [col["key"] for col in columns_table.all()]:
                st.warning(f"Invalid filter key \"{key}\". Will be matched as full text.")
