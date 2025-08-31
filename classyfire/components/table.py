import streamlit as st

from .filters import filter_entries, filters_include, filters_exclude
from .sort import sort_entries
from ..database import columns_table, entries_table, update_database, add_new_entry
from ..i18n import t


def get_columns_visibility() -> dict[str, bool]:
    st.subheader(f"🏛️ {t('Visible columns')}")

    if "columns_visibility" not in st.session_state:
        st.session_state.columns_visibility = {col["key"]: True for col in columns_table.all()}
    if "columns_visibility_key" not in st.session_state:
        st.session_state.columns_visibility_key = 0

    columns_visibility = st.session_state.columns_visibility

    options: list[dict] = [
        {
            "label": t("All"),
            "button_type": "primary",
            "columns": [col["key"] for col in columns_table.all()],
            "row_height": None,
        },
        {
            "label": t("Only results"),
            "button_type": "secondary",
            "columns": ["reference", "results"],
            "row_height": 100,
        },
        {
            "label": t("Only highlights"),
            "button_type": "secondary",
            "columns": ["reference", "highlights"],
            "row_height": 100,
        },
    ]
    st_cols = st.columns(len(options))
    for i, option in enumerate(options):
        if st_cols[i].button(option["label"], type=option["button_type"], use_container_width=True):
            columns_visibility = {col["key"]: col["key"] in option["columns"] for col in columns_table.all()}
            st.session_state.columns_visibility = columns_visibility
            st.session_state.columns_visibility_key += 1
            st.session_state.table_row_height = option["row_height"]

    with st.expander(t("Show column toggles")):
        return {
            col["key"]: st.toggle(
                col["label"],
                value=columns_visibility[col["key"]],
                key=f"columns_visibility_{i}_{st.session_state.columns_visibility_key}",
            )
            for i, col in enumerate(columns_table.all())
        }


def main() -> None:
    if "table_key" not in st.session_state:
        st.session_state.table_key = 0
    if "table_row_height" not in st.session_state:
        st.session_state.table_row_height = None

    columns_visibility = get_columns_visibility()

    st.divider()
    st.subheader(f"📅 {t('Table')}")

    entries = entries_table.all()
    filtered_entries = sort_entries(filter_entries(entries))
    st.write(f"_{t('Showing')} {len(filtered_entries)} {t('of')} {len(entries)} {t('entries')}._")
    st.caption(t("table_caption"))

    if len(filters_include) > 0:
        st.info(t("clear_filters_info"))
    else:
        if st.button(
            t("Add new entry"), type="primary", key=f"table_add_{st.session_state.table_key}", use_container_width=True
        ):
            add_new_entry()
            st.session_state.table_key += 1
            st.rerun()

    filtered_entries_with_view = []
    for entry in filtered_entries:
        doc_id = entry.doc_id
        entry = dict(entry)
        entry["view"] = f"?doc_id={doc_id}"
        entry["doc_id"] = doc_id
        filtered_entries_with_view.append(entry)

    column_config = {
        col["key"]: st.column_config.ListColumn(col["label"]) if col["type"] == "tag" else col["label"]
        for col in columns_table.all()
    }
    column_config.update({
        "view": st.column_config.LinkColumn(
            "",
            display_text=t("View"),
            disabled=True,
        ),
    })
    column_order = ["view"] + [col["key"] for col in columns_table.all() if columns_visibility[col["key"]]]

    updated_entries = st.data_editor(
        filtered_entries_with_view,
        column_config=column_config,
        column_order=column_order,
        num_rows="dynamic" if len(filters_include) == 0 and len(filters_exclude) == 0 else "fixed",
        row_height=st.session_state.table_row_height,
        height=500,
        key=f"table_{st.session_state.table_key}",
    )

    for entry in updated_entries:
        if "view" in entry:
            del entry["view"]
        if "doc_id" in entry:
            del entry["doc_id"]

        for col in columns_table.all():
            if entry.get(col["key"]) is None:
                if col["type"] == "tags":
                    entry[col["key"]] = []
                else:
                    entry[col["key"]] = ""

    def discard_callback() -> None:
        st.session_state.table_key += 1

    update_database(filtered_entries, updated_entries, discard_callback=discard_callback)
