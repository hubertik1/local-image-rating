import streamlit as st

from ..constants import (
    DEFAULT_EMOTIONS,
    EMOTIONS_LEFT_COLUMN_COUNT,
    OPTION_BEST_OF_THREE_LABEL,
    OPTION_EMOTIONS_LABEL,
    OPTION_QUALITY_LABEL,
    OPTION_TRIPLET_QUALITY_LABEL,
    TEST_OPTION_BEST_OF_THREE,
    TEST_OPTION_EMOTIONS,
    TEST_OPTION_QUALITY,
    TEST_OPTION_TRIPLET_QUALITY,
    TRIPLET_IMAGE_COUNT,
)
from ..dialogs import request_error_alert
from ..state import start_session
from ..storage import (
    build_random_image_groups,
    build_triplet_image_groups,
    get_image_paths,
    group_images_by_folder,
)
from ..styles import sync_keyboard_shortcuts


def render_setup_screen() -> None:
    sync_keyboard_shortcuts(False)
    st.title("Image Rating App")

    all_image_paths = get_image_paths()
    folder_images = group_images_by_folder(all_image_paths)
    folder_options = [None, *folder_images]
    if st.session_state.get("draft_image_folder") not in folder_options:
        st.session_state.draft_image_folder = None

    def format_folder(folder: str | None) -> str:
        if folder is None:
            return "All folders"
        label = "Main folder" if folder == "." else folder
        return f"{label} ({len(folder_images[folder])} images)"

    with st.sidebar:
        st.header("Browse folders")
        selected_folder = st.selectbox(
            "Folder to evaluate",
            options=folder_options,
            format_func=format_folder,
            key="draft_image_folder",
            help="Choose a category in new_images. Each nested folder is listed separately.",
        )
        image_paths = (
            all_image_paths if selected_folder is None else folder_images[selected_folder]
        )
        st.caption(f"{len(image_paths)} images available")

    triplet_groups, incomplete_triplet_groups = build_triplet_image_groups(image_paths)
    if not image_paths:
        st.warning("No images found in new_images")

    left_col, right_col = st.columns([1, 1], gap="large")
    with left_col:
        st.text_input("Name", key="draft_name")
        selected_option_label = st.radio(
            "Choose test",
            options=[
                OPTION_QUALITY_LABEL,
                OPTION_EMOTIONS_LABEL,
                OPTION_TRIPLET_QUALITY_LABEL,
                OPTION_BEST_OF_THREE_LABEL,
            ],
            key="draft_option",
        )
        start_disabled = (
            len(triplet_groups) == 0
            if selected_option_label == OPTION_TRIPLET_QUALITY_LABEL
            else len(image_paths) == 0
        )
        if selected_option_label not in {
            OPTION_TRIPLET_QUALITY_LABEL,
            OPTION_BEST_OF_THREE_LABEL,
        }:
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
        elif selected_option_label == OPTION_TRIPLET_QUALITY_LABEL:
            st.write("3-image sets:")
            st.info(f"Sets found: {len(triplet_groups)}")
            if incomplete_triplet_groups:
                preview = ", ".join(incomplete_triplet_groups[:5])
                extra_count = len(incomplete_triplet_groups) - 5
                suffix = f" and {extra_count} more" if extra_count > 0 else ""
                st.warning(
                    "Some sets have fewer than 3 images and will still be shown: "
                    f"{preview}{suffix}"
                )
        elif selected_option_label == OPTION_BEST_OF_THREE_LABEL:
            selected_folders = group_images_by_folder(image_paths)
            group_count = sum(
                (len(paths) + TRIPLET_IMAGE_COUNT - 1) // TRIPLET_IMAGE_COUNT
                for paths in selected_folders.values()
            )
            st.write("Best-image selection:")
            st.info(
                f"{len(image_paths)} images will be shuffled within their folders into "
                f"{group_count} sets of up to 3. Sets never mix folders."
            )
            if any(len(paths) % TRIPLET_IMAGE_COUNT for paths in selected_folders.values()):
                st.caption("Any remaining 1 or 2 images stay in a separate set from their own folder.")

    if start_clicked:
        errors: list[str] = []
        user_name = st.session_state.get("draft_name", "").strip()
        if selected_option_label == OPTION_EMOTIONS_LABEL:
            test_option = TEST_OPTION_EMOTIONS
        elif selected_option_label == OPTION_TRIPLET_QUALITY_LABEL:
            test_option = TEST_OPTION_TRIPLET_QUALITY
        elif selected_option_label == OPTION_BEST_OF_THREE_LABEL:
            test_option = TEST_OPTION_BEST_OF_THREE
        else:
            test_option = TEST_OPTION_QUALITY
        show_labels = (
            False
            if test_option in {
                TEST_OPTION_TRIPLET_QUALITY,
                TEST_OPTION_BEST_OF_THREE,
            }
            else bool(st.session_state.get("draft_show_labels", False))
        )

        if not user_name:
            errors.append("Name is required.")
        if test_option == TEST_OPTION_EMOTIONS and not selected_emotions:
            errors.append("Select at least one emotion.")
        if test_option == TEST_OPTION_TRIPLET_QUALITY and not triplet_groups:
            errors.append("No image sets ending with _1, _2 or _3 found in new_images.")
        if not image_paths:
            errors.append("No images found in new_images.")

        if errors:
            request_error_alert("\n".join(errors))
        else:
            session_image_groups = triplet_groups
            if test_option == TEST_OPTION_BEST_OF_THREE:
                session_image_groups = build_random_image_groups(image_paths)

            start_session(
                user_name,
                test_option,
                selected_emotions,
                image_paths,
                show_labels,
                session_image_groups,
            )
