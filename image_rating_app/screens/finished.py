import streamlit as st

from ..state import reset_session
from ..styles import sync_keyboard_shortcuts


def render_finished_screen() -> None:
    sync_keyboard_shortcuts(False)
    st.markdown("<div style='padding-top: 0.8rem;'></div>", unsafe_allow_html=True)
    st.success("Results saved.")
    st.write(f"Number of saved ratings: {st.session_state.saved_rows}")
    st.write(f"CSV file: `{st.session_state.saved_csv_path}`")
    if st.button("New session", type="primary"):
        reset_session()
