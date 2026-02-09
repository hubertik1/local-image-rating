import streamlit as st

from .dialogs import render_error_alert_dialog
from .screens import render_finished_screen, render_rating_screen, render_setup_screen
from .state import init_state, reset_session
from .storage import ensure_dirs
from .styles import inject_custom_button_styles


def run_app() -> None:
    st.set_page_config(page_title="Image Rating App", layout="wide")
    inject_custom_button_styles()
    ensure_dirs()
    init_state()

    if st.session_state.error_alert_message:
        render_error_alert_dialog()

    phase = st.session_state.phase
    if phase == "setup":
        render_setup_screen()
    elif phase == "rating":
        render_rating_screen()
    elif phase == "finished":
        render_finished_screen()
    else:
        reset_session()
