from tinydb import TinyDB, Query

from classyfire.config import DB_PATH, DEFAULT_COLUMNS


db = TinyDB(DB_PATH)
columns_table = db.table("columns")
entries_table = db.table("entries")


def init_columns():
    if len(columns_table.all()) == 0:
        columns_table.insert_multiple(DEFAULT_COLUMNS)


def init_entries():
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


init_columns()
init_entries()
filters_options = get_filters_options(columns_table, entries_table)
