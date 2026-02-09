from pathlib import Path

import streamlit as st


def init_state() -> None:
    defaults = {
        "phase": "setup",
        "name": "",
        "test_option": "emotions",
        "show_labels": False,
        "selected_emotions": [],
        "images": [],
        "current_index": 0,
        "ratings": {},
        "draft_ratings": {},
        "saved_csv_path": "",
        "saved_rows": 0,
        "finish_confirm_visible": False,
        "error_alert_message": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def start_session(
    name: str,
    test_option: str,
    selected_emotions: list[str],
    images: list[Path],
    show_labels: bool,
) -> None:
    st.session_state.phase = "rating"
    st.session_state.name = name
    st.session_state.test_option = test_option
    st.session_state.show_labels = show_labels
    st.session_state.rating_show_labels = show_labels
    st.session_state.selected_emotions = selected_emotions
    st.session_state.images = [str(path) for path in images]
    st.session_state.current_index = 0
    st.session_state.ratings = {}
    st.session_state.draft_ratings = {}
    st.session_state.saved_csv_path = ""
    st.session_state.saved_rows = 0
    st.session_state.finish_confirm_visible = False
    st.rerun()


def reset_session() -> None:
    st.session_state.clear()
    st.rerun()
