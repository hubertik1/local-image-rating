import streamlit as st

from .storage import save_results_csv


def request_finish_confirmation() -> None:
    st.session_state.finish_confirm_visible = True
    st.rerun()


def request_error_alert(message: str) -> None:
    st.session_state.error_alert_message = message
    st.session_state.finish_confirm_visible = False
    st.rerun()


def _render_error_alert_inline() -> None:
    st.error(st.session_state.error_alert_message)
    if st.button("OK", key="error_alert_ok_inline", type="primary"):
        st.session_state.error_alert_message = ""
        st.rerun()


if hasattr(st, "dialog"):

    @st.dialog("Error")
    def render_error_alert_dialog() -> None:
        st.write(st.session_state.error_alert_message)
        if st.button("OK", key="error_alert_ok_dialog", type="primary"):
            st.session_state.error_alert_message = ""
            st.rerun()

else:

    def render_error_alert_dialog() -> None:
        _render_error_alert_inline()


def _render_finish_confirmation_inline() -> None:
    st.warning("Are you sure you want to finish and save current ratings?")
    confirm_col, cancel_col = st.columns(2)
    with confirm_col:
        if st.button("Yes, finish and save", type="primary", key="confirm_finish_inline"):
            save_results_csv()
            st.rerun()
    with cancel_col:
        _, cancel_right_col = st.columns([0.52, 0.48])
        with cancel_right_col:
            if st.button("Cancel", key="cancel_finish_inline", use_container_width=True):
                st.session_state.finish_confirm_visible = False
                st.rerun()


if hasattr(st, "dialog"):

    @st.dialog("Confirm finish")
    def render_finish_confirmation_dialog() -> None:
        st.write("Are you sure you want to finish and save current ratings?")
        confirm_col, cancel_col = st.columns(2)
        with confirm_col:
            if st.button(
                "Yes, finish and save",
                type="primary",
                key="confirm_finish_dialog",
            ):
                save_results_csv()
                st.rerun()
        with cancel_col:
            _, cancel_right_col = st.columns([0.52, 0.48])
            with cancel_right_col:
                if st.button(
                    "Cancel",
                    key="cancel_finish_dialog",
                    use_container_width=True,
                ):
                    st.session_state.finish_confirm_visible = False
                    st.rerun()

else:

    def render_finish_confirmation_dialog() -> None:
        _render_finish_confirmation_inline()
