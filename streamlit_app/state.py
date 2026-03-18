from __future__ import annotations

from typing import Any

import streamlit as st

DEFAULT_STATE: dict[str, Any] = {
    "selected_table": None,
    "last_question": "",
    "last_answer": None,
    "last_error": None,
    "backend_status": None,
    "tables_payload": None,
    "table_profile": None,
}


def initialize_state() -> None:
    for key, value in DEFAULT_STATE.items():
        st.session_state.setdefault(key, value)
