import streamlit as st

from ..database import columns_table, get_filters_options


filters_include: list[str] = []
filters_exclude: list[str] = []


def filter_entries(entries):
    for filter in filters_include:
        if ":" in filter:
            key, value = filter.split(":", 1)
            if key in [col["key"] for col in columns_table.all()]:
                entries = [
                    entry for entry in entries if value.lower() in [tag.lower() for tag in entry.get(key, []) or []]
                ]
                continue

        entries = [entry for entry in entries if any(filter.lower() in str(v).lower() for v in entry.values())]

    for filters in filters_exclude:
        if ":" in filters:
            key, value = filters.split(":", 1)
            if key in [col["key"] for col in columns_table.all()]:
                entries = [
                    entry for entry in entries if value.lower() not in [tag.lower() for tag in entry.get(key, []) or []]
                ]
                continue

        entries = [entry for entry in entries if all(filters.lower() not in str(v).lower() for v in entry.values())]

    return entries


def clear_filters():
    filters_include.clear()
    st.session_state.filters_key += 1
    st.rerun()


def main():
    st.write("## 🧩 Filters")
    st.write(
        "Filter by text or tags. Use the `tag-type:tag-value` syntax to filter by specific tags (_e.g.,_ `authors:johnson`)."
    )

    if "filters_key" not in st.session_state:
        st.session_state.filters_key = 0

    filters_options = get_filters_options()

    filters_include[:] = st.multiselect(
        "Include",
        filters_options,
        placeholder="Add filters",
        accept_new_options=True,
        key=f"filters_include_{st.session_state.filters_key}",
    )

    filters_exclude[:] = st.multiselect(
        "Exclude",
        filters_options,
        placeholder="Add filters",
        accept_new_options=True,
        key=f"filters_exclude_{st.session_state.filters_key}",
    )

    for filter in filters_include + filters_exclude:
        if ":" in filter:
            key, _ = filter.split(":", 1)
            if key not in [col["key"] for col in columns_table.all()]:
                st.warning(f'Invalid tag type "`{key}:`". Will be matched as full text.')

    if st.button("Clear filters", type="secondary", use_container_width=True):
        clear_filters()
