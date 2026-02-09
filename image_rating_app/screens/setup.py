import streamlit as st

from ..constants import (
    DEFAULT_EMOTIONS,
    EMOTIONS_LEFT_COLUMN_COUNT,
    OPTION_EMOTIONS_LABEL,
    OPTION_QUALITY_LABEL,
)
from ..dialogs import request_error_alert
from ..state import start_session
from ..storage import get_image_paths
from ..styles import sync_keyboard_shortcuts


def render_setup_screen() -> None:
    sync_keyboard_shortcuts(False)
    st.title("Image Rating App")

    image_paths = get_image_paths()
    if not image_paths:
        st.warning("No images found in new_images")

    left_col, right_col = st.columns([1, 1], gap="large")
    start_disabled = len(image_paths) == 0
    with left_col:
        st.text_input("Name", key="draft_name")
        selected_option_label = st.radio(
            "Choose test",
            options=[OPTION_QUALITY_LABEL, OPTION_EMOTIONS_LABEL],
            key="draft_option",
        )
        st.checkbox("Show labels", key="draft_show_labels", value=False)
        start_clicked = st.button("Start", type="primary", disabled=start_disabled)

    selected_emotions: list[str] = []
    with right_col:
        if selected_option_label == OPTION_EMOTIONS_LABEL:
            st.write("Choose emotions:")
            emotions_left_col, emotions_right_col = st.columns(2, gap="medium")
            for idx, emotion in enumerate(DEFAULT_EMOTIONS):
                target_col = (
                    emotions_left_col
                    if idx < EMOTIONS_LEFT_COLUMN_COUNT
                    else emotions_right_col
                )
                with target_col:
                    if st.checkbox(
                        emotion,
                        value=idx < EMOTIONS_LEFT_COLUMN_COUNT,
                        key=f"draft_emotion_{idx}",
                    ):
                        selected_emotions.append(emotion)

    if start_clicked:
        errors: list[str] = []
        user_name = st.session_state.get("draft_name", "").strip()
        test_option = (
            "emotions"
            if selected_option_label == OPTION_EMOTIONS_LABEL
            else "quality"
        )
        show_labels = bool(st.session_state.get("draft_show_labels", False))

        if not user_name:
            errors.append("Name is required.")
        if test_option == "emotions" and not selected_emotions:
            errors.append("Select at least one emotion.")
        if not image_paths:
            errors.append("No images found in new_images.")

        if errors:
            request_error_alert("\n".join(errors))
        else:
            start_session(
                user_name,
                test_option,
                selected_emotions,
                image_paths,
                show_labels,
            )
