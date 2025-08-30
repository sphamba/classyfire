from tinydb import TinyDB, Query
import streamlit as st

from classyfire.config import DB_PATH, DEFAULT_COLUMNS


db = TinyDB(DB_PATH)

columns_table = db.table("columns")
if len(columns_table.all()) == 0:
    columns_table.insert_multiple(DEFAULT_COLUMNS)

entries_table = db.table("entries")
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
            "reference": "Smith et al. (2024)",
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


def get_filters_options(columns_table, entries_table):
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


def filter_entries(entries, filters):
    for filter in filters:
        if ":" in filter:
            key, value = filter.split(":", 1)
            if key in [col["key"] for col in columns_table.all()]:
                entries = [entry for entry in entries if value.lower() in [tag.lower() for tag in entry.get(key, []) or []]]
                continue

        entries = [entry for entry in entries if any(filter.lower() in str(v).lower() for v in entry.values())]

    return entries


st.set_page_config(
    page_title="ClassyFire",
    page_icon="🧐",
    layout="wide",
    menu_items={
        "Get help": "https://github.com/sphamba/classyfire/issues",
        "Report a bug": "https://github.com/sphamba/classyfire/issues",
        "About": "Classify research articles",
    },
)
st.write("# ClassyFire")

filters_options = get_filters_options(columns_table, entries_table)
filters = st.multiselect(
    "Filters",
    filters_options,
    placeholder="Filter by text or tags",
    accept_new_options=True,
)
for filter in filters:
    if ":" in filter:
        key, value = filter.split(":", 1)
        if key not in [col["key"] for col in columns_table.all()]:
            st.warning(f"Invalid filter key \"{key}\". Will be matched as full text.")

entries = entries_table.all()
filtered_entries = filter_entries(entries, filters)
st.write(f"Showing {len(filtered_entries)} of {len(entries)} entries.")
if "table_key" not in st.session_state:
    st.session_state.table_key = 0
updated_entries = st.data_editor(
    filtered_entries,
    column_config={ col["key"]: col["label"] for col in columns_table.all() },
    num_rows="dynamic" if len(filters) == 0 else "fixed",
    key=st.session_state.table_key
)

if len(filters) > 0:
    st.info("Clear filters to add or remove entries.")

if [dict(entry) for entry in filtered_entries] != updated_entries:
    if st.button("Save changes", type="primary"):
        entries_table.remove(doc_ids=[entry.doc_id for entry in filtered_entries])
        entries_table.insert_multiple(updated_entries)
        st.rerun()

    if st.button("Discard changes", type="secondary"):
        st.session_state.table_key += 1
        st.rerun()
