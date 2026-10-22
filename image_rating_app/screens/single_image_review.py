from pathlib import Path

import streamlit as st

from ..constants import SINGLE_IMAGE_REVIEW_CHOICES
from ..dialogs import render_finish_confirmation_dialog, request_finish_confirmation
from ..routing import PAGE_RATING, navigate_to
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
    heading_col, finish_col = st.columns([4, 1], vertical_alignment="center")
    with heading_col:
        st.subheader(f"Review image {current_index + 1} of {total}")
        folder = get_image_folder_key(current_image)
        st.caption(f"Folder: {'Main folder' if folder == '.' else folder}")
    with finish_col:
        if st.button("Finish and save CSV", key="finish_btn", width="stretch"):
            request_finish_confirmation()

    image_col, choices_col = st.columns([3, 1], gap="large")
    image_exists = current_image.is_file()
    with image_col:
        st.caption(f"File name: `{current_image.name}`")
        with st.container(key="single_image_review_image"):
            if image_exists:
                st.image(str(current_image), width="stretch")
            else:
                st.error(f"Cannot load image: {current_image.name}")

    with choices_col:
        st.write("Choose a rating")
        st.caption("Click a choice or press 1, 2, or 3 to rate and continue.")
        for shortcut, (choice_key, label) in enumerate(SINGLE_IMAGE_REVIEW_CHOICES, start=1):
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
        if saved_rating:
            st.caption(f"Saved rating: {saved_rating}")
        st.caption("Delete is a rating; original image files are kept.")
        if st.button(
            "Previous",
            key="previous_btn",
            disabled=current_index == 0 or confirming_finish,
            width="stretch",
        ):
            navigate_to(PAGE_RATING, current_index - 1)
