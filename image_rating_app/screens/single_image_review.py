from pathlib import Path

import streamlit as st

from ..constants import SINGLE_IMAGE_REVIEW_CHOICES
from ..dialogs import render_finish_confirmation_dialog, request_finish_confirmation
from ..routing import PAGE_RATING, PAGE_SETUP, navigate_to
from ..state import reset_session
from ..storage import get_image_folder_key, get_image_key
from ..styles import sync_keyboard_shortcuts


def render_single_image_review_screen() -> None:
    sync_keyboard_shortcuts(False)
    images = [Path(path) for path in st.session_state.images]
    total = len(images)
    if total == 0:
        st.warning("No images to review. Return to the start screen.")
        if st.button("New session"):
            reset_session()
        return

    current_index = st.session_state.current_index
    if st.session_state.finish_confirm_visible:
        render_finish_confirmation_dialog()
    confirming_finish = st.session_state.finish_confirm_visible

    if current_index >= total:
        if st.button("← Back to setup", key="back_to_setup_btn"):
            navigate_to(PAGE_SETUP)
        st.success("You have reached the end of the images.")
        st.info(f"Rated images: {len(st.session_state.ratings)} of {total}")
        previous_col, finish_col = st.columns(2)
        with previous_col:
            if st.button("Previous", key="previous_btn", disabled=confirming_finish, width="stretch"):
                navigate_to(PAGE_RATING, total - 1)
        with finish_col:
            if st.button("Finish and save CSV", key="finish_all_btn", type="primary", width="stretch"):
                request_finish_confirmation()
        return

    current_image = images[current_index]
    image_key = get_image_key(current_image)
    saved_rating = st.session_state.ratings.get(image_key, {}).get("rating")
    with st.container(key="single_image_review_header"):
        back_col, heading_col, finish_col = st.columns([1, 4, 1], gap="small", vertical_alignment="center")
        with back_col:
            if st.button("← Back to setup", key="back_to_setup_btn", disabled=confirming_finish, width="stretch"):
                navigate_to(PAGE_SETUP)
        with heading_col:
            st.subheader(f"Review image {current_index + 1} of {total}")
            folder = get_image_folder_key(current_image)
            st.caption(f"Folder: {'Main folder' if folder == '.' else folder} · File: {current_image.name}")
        with finish_col:
            if st.button("Finish and save CSV", key="finish_btn", width="stretch"):
                request_finish_confirmation()

    image_exists = current_image.is_file()
    with st.container(key="single_image_review_image"):
        if image_exists:
            st.image(str(current_image), width="stretch")
        else:
            st.error(f"Cannot load image: {current_image.name}")

    with st.container(key="single_image_review_controls"):
        choice_columns = st.columns([1, 1.7, 1], gap="small")
        for shortcut, (choice_key, label) in enumerate(SINGLE_IMAGE_REVIEW_CHOICES, start=1):
            with choice_columns[shortcut - 1], st.container(key=f"single_review_choice_{choice_key}"):
                if st.button(
                    label,
                    key=f"single_image_review_{current_index}_{choice_key}",
                    type="primary" if saved_rating == label else "secondary",
                    shortcut=str(shortcut),
                    disabled=not image_exists or confirming_finish,
                    width="stretch",
                ):
                    st.session_state.ratings[image_key] = {"rating": label}
                    navigate_to(PAGE_RATING, current_index + 1)
        previous_col, status_col = st.columns([1, 5], gap="small", vertical_alignment="center")
        with previous_col:
            if st.button(
                "Previous",
                key="previous_btn",
                disabled=current_index == 0 or confirming_finish,
                width="stretch",
            ):
                navigate_to(PAGE_RATING, current_index - 1)
        with status_col:
            st.caption(f"Saved rating: {saved_rating}" if saved_rating else "Click a choice or press 1, 2, or 3 to rate and continue.")
            st.caption("Delete is a rating; original image files are kept.")
