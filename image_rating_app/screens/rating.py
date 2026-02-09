from pathlib import Path
import html

import streamlit as st

from ..dialogs import (
    render_finish_confirmation_dialog,
    request_error_alert,
    request_finish_confirmation,
)
from ..state import reset_session
from ..storage import get_image_key, get_image_label
from ..styles import sync_keyboard_shortcuts


def format_quality_option(value: str) -> str:
    labels = {
        "1": "1 (good image)",
        "0.5": "0.5 (partially good image)",
        "0": "0 (reject image)",
    }
    return labels.get(value, value)


def render_emotions_form(current_index: int) -> tuple[bool, dict[str, int], str]:
    st.markdown(
        """
        <style>
        /* Compact radio blocks for emotion ratings */
        div[data-testid="stRadio"] {
            margin: 0 !important;
            padding: 0 !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] {
            flex-wrap: nowrap !important;
            gap: 0.22rem !important;
        }
        div[data-testid="stRadio"] label[data-baseweb="radio"] {
            margin-right: 0 !important;
        }
        div[data-testid="stRadio"] label[data-baseweb="radio"] p {
            font-size: 0.9rem !important;
        }
        /* Tighter vertical spacing between emotion rows */
        div[class*="st-key-emotion_score_"] {
            margin-top: -0.36rem !important;
            margin-bottom: -0.36rem !important;
        }
        div[class*="st-key-emotion_score_"] div[data-testid="stRadio"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    selected_emotions: list[str] = st.session_state.selected_emotions
    raw_values: dict[str, int | None] = {}

    for emotion_idx, emotion in enumerate(selected_emotions):
        key = f"emotion_score_{current_index}_{emotion_idx}"
        label_col, rating_col = st.columns([0.30, 0.70], gap="small")
        with label_col:
            st.markdown(
                f"<div style='padding-top:0.28rem; white-space: nowrap;'>{emotion}</div>",
                unsafe_allow_html=True,
            )
        with rating_col:
            raw_values[emotion] = st.radio(
                label=f"{emotion} rating",
                options=[1, 2, 3, 4, 5, 6, 7],
                index=None,
                horizontal=True,
                key=key,
                label_visibility="collapsed",
            )

    if any(value is None for value in raw_values.values()):
        return False, {}, "Set a score for all emotions."

    values = {emotion: int(value) for emotion, value in raw_values.items() if value is not None}
    return True, values, ""


def render_quality_form(current_index: int) -> tuple[bool, dict[str, str], str]:
    quality_score = st.radio(
        "Quality score",
        options=["1", "0.5", "0"],
        format_func=format_quality_option,
        index=None,
        horizontal=True,
        key=f"quality_score_{current_index}",
    )
    comment = st.text_area(
        "Comment (optional)",
        key=f"quality_comment_{current_index}",
    )

    if quality_score is None:
        return False, {"quality_score": "", "comment": comment}, "Select a quality score."
    return True, {"quality_score": quality_score, "comment": comment}, ""


def store_current_draft(current_path: Path, current_index: int) -> None:
    image_key = get_image_key(current_path)

    if st.session_state.test_option == "emotions":
        emotion_values: dict[str, int] = {}
        for emotion_idx, emotion in enumerate(st.session_state.selected_emotions):
            key = f"emotion_score_{current_index}_{emotion_idx}"
            value = st.session_state.get(key)
            if value in {1, 2, 3, 4, 5, 6, 7}:
                emotion_values[emotion] = int(value)
        st.session_state.draft_ratings[image_key] = {
            "emotion_values": emotion_values,
        }
    else:
        quality_key = f"quality_score_{current_index}"
        comment_key = f"quality_comment_{current_index}"
        quality_score = st.session_state.get(quality_key)
        comment = st.session_state.get(comment_key, "")

        st.session_state.draft_ratings[image_key] = {
            "quality_score": quality_score if quality_score in {"1", "0.5", "0"} else "",
            "comment": comment if isinstance(comment, str) else "",
        }


def hydrate_form_state_from_saved_rating(current_path: Path, current_index: int) -> None:
    image_key = get_image_key(current_path)
    saved_record = st.session_state.ratings.get(image_key)
    if saved_record is None:
        saved_record = st.session_state.draft_ratings.get(image_key, {})

    if st.session_state.test_option == "emotions":
        saved_values: dict[str, int] = saved_record.get("emotion_values", {})
        for emotion_idx, emotion in enumerate(st.session_state.selected_emotions):
            key = f"emotion_score_{current_index}_{emotion_idx}"
            saved_value = saved_values.get(emotion)
            if key not in st.session_state and saved_value in {1, 2, 3, 4, 5, 6, 7}:
                st.session_state[key] = saved_value
    else:
        quality_key = f"quality_score_{current_index}"
        comment_key = f"quality_comment_{current_index}"
        saved_score = saved_record.get("quality_score")
        saved_comment = saved_record.get("comment", "")

        normalized_score: str | None = None
        if saved_score in {"1", 1, 1.0}:
            normalized_score = "1"
        elif saved_score in {"0.5", 0.5}:
            normalized_score = "0.5"
        elif saved_score in {"0", 0, 0.0}:
            normalized_score = "0"

        if quality_key not in st.session_state and normalized_score is not None:
            st.session_state[quality_key] = normalized_score
        if comment_key not in st.session_state and isinstance(saved_comment, str):
            st.session_state[comment_key] = saved_comment


def render_rating_screen() -> None:
    images = [Path(path) for path in st.session_state.images]
    total = len(images)

    if total == 0:
        sync_keyboard_shortcuts(False)
        st.warning("No images to rate. Return to the start screen.")
        if st.button("New session"):
            reset_session()
        return

    current_index = st.session_state.current_index
    if st.session_state.finish_confirm_visible:
        render_finish_confirmation_dialog()

    if current_index >= total:
        sync_keyboard_shortcuts(False)
        st.markdown("<div style='padding-top: 0.8rem;'></div>", unsafe_allow_html=True)
        st.success("No more images")
        st.info(f"Rated images: {len(st.session_state.ratings)} of {total}")
        if st.button("Finish and save CSV", type="primary", key="finish_all_btn"):
            request_finish_confirmation()
        return

    current_path = images[current_index]
    hydrate_form_state_from_saved_rating(current_path, current_index)
    left_col, _, right_col = st.columns([1.22, 0.08, 0.88], gap="medium")
    finish_clicked = False
    previous_clicked = False
    next_clicked = False

    with left_col:
        if "rating_show_labels" not in st.session_state:
            st.session_state.rating_show_labels = st.session_state.get("show_labels", False)
        show_labels_now = bool(st.session_state.get("rating_show_labels", False))
        image_label = get_image_label(current_path)
        content_col, _ = st.columns([10, 0.05], gap="small")
        with content_col:
            header_image_col, header_label_col = st.columns([0.64, 0.36], gap="small")
            with header_image_col:
                st.subheader(f"Image {current_index + 1} of {total}")
            with header_label_col:
                if show_labels_now and image_label:
                    st.markdown(
                        (
                            "<div style='font-size:1.5rem; font-weight:600; "
                            "text-align:right; line-height:1.2; margin-top:1.2rem;'>"
                            f"Label: <span style='color:#1d4ed8;'>{html.escape(image_label)}</span></div>"
                        ),
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown("&nbsp;", unsafe_allow_html=True)

            file_col, show_labels_col = st.columns([1.0, 0.20], gap="small")
            with file_col:
                st.caption(f"File name: `{current_path.name}`")
            with show_labels_col:
                st.checkbox("Show labels", key="rating_show_labels")

            st.session_state.show_labels = bool(st.session_state.get("rating_show_labels", False))
            if current_path.exists():
                st.image(str(current_path), use_container_width=True)
            else:
                st.error(f"Cannot load image: {current_path.name}")

    with right_col:
        st.markdown(
            "<h3 style='margin: 0 0 0.02rem 0;'>Ratings</h3>",
            unsafe_allow_html=True,
        )
        if st.session_state.test_option == "emotions":
            st.markdown(
                "<div style='margin: 0 0 -0.5rem 0;'>Emotion rating (1-7):</div>",
                unsafe_allow_html=True,
            )
            is_valid, payload, error_message = render_emotions_form(current_index)
        else:
            is_valid, payload, error_message = render_quality_form(current_index)

    btn_left_col, _, btn_right_col = st.columns([1.22, 0.08, 0.88], gap="medium")
    with btn_left_col:
        finish_clicked = st.button("Finish", key="finish_btn")

    with btn_right_col:
        col_previous, _, col_next = st.columns([1, 1.5, 1])
        with col_previous:
            previous_clicked = st.button(
                "Previous",
                key="previous_btn",
                disabled=current_index == 0,
            )
        with col_next:
            next_clicked = st.button("Next", key="next_btn", type="primary")

    sync_keyboard_shortcuts(
        not st.session_state.finish_confirm_visible
        and not bool(st.session_state.error_alert_message)
    )

    if previous_clicked:
        st.session_state.finish_confirm_visible = False
        store_current_draft(current_path, current_index)
        if current_index > 0:
            st.session_state.current_index = current_index - 1
        st.rerun()

    if next_clicked:
        st.session_state.finish_confirm_visible = False
        if not is_valid:
            request_error_alert(error_message)
        else:
            image_key = get_image_key(current_path)
            if st.session_state.test_option == "emotions":
                st.session_state.ratings[image_key] = {
                    "emotion_values": payload,
                }
            else:
                st.session_state.ratings[image_key] = {
                    "quality_score": payload["quality_score"],
                    "comment": payload["comment"],
                }
            st.session_state.draft_ratings.pop(image_key, None)
            st.session_state.current_index = current_index + 1
            st.rerun()

    if finish_clicked:
        request_finish_confirmation()
