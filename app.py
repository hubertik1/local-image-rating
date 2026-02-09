from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import unicodedata

import pandas as pd
import streamlit as st

IMAGE_DIR = Path("new_images")
OUTPUT_DIR = Path("output")
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
DEFAULT_EMOTIONS = [
    "amusement",
    "anger",
    "attachment love",
    "awe",
    "craving",
    "disgust",
    "excitement",
    "fear",
    "joy",
    "neutral",
    "nurturant love",
    "sadness",
]
OPTION_EMOTIONS_LABEL = "Emotion-based rating"
OPTION_QUALITY_LABEL = "Quality rating"


def inject_custom_button_styles() -> None:
    st.markdown(
        """
        <style>
        /* Reduce top whitespace across all Streamlit views */
        [data-testid="stAppViewContainer"] > .main {
            padding-top: calc(1.7rem) !important;
        }
        .block-container {
            padding-top: calc(1.7rem) !important;
        }

        /* Finish button: red text + red border */
        .st-key-finish_btn button,
        button[id*="finish_btn"] {
            color: #b91c1c !important;
            border: 1px solid #b91c1c !important;
            background-color: #ffffff !important;
        }
        .st-key-finish_btn button:hover,
        button[id*="finish_btn"]:hover {
            background-color: #fef2f2 !important;
            color: #991b1b !important;
            border-color: #991b1b !important;
        }

        /* Confirm button in finish alert: red */
        .st-key-confirm_finish_dialog button,
        .st-key-confirm_finish_inline button,
        button[id*="confirm_finish_dialog"],
        button[id*="confirm_finish_inline"] {
            color: #ffffff !important;
            border: 1px solid #b91c1c !important;
            background-color: #dc2626 !important;
        }
        .st-key-confirm_finish_dialog button:hover,
        .st-key-confirm_finish_inline button:hover,
        button[id*="confirm_finish_dialog"]:hover,
        button[id*="confirm_finish_inline"]:hover {
            background-color: #b91c1c !important;
            border-color: #991b1b !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_dirs() -> None:
    IMAGE_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)


def get_image_paths() -> list[Path]:
    ensure_dirs()
    images = [
        path
        for path in IMAGE_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(images, key=lambda p: p.name.lower())


def normalize_ascii(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return normalized.encode("ascii", "ignore").decode("ascii")


def sanitize_for_filename(name: str) -> str:
    replaced = re.sub(r"\s+", "_", name.strip())
    ascii_value = normalize_ascii(replaced)
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", ascii_value)
    safe = re.sub(r"_+", "_", safe).strip("_")
    return safe or "user"


def sanitize_for_column(name: str) -> str:
    lowered = name.strip().lower().replace(" ", "_")
    ascii_value = normalize_ascii(lowered)
    safe = re.sub(r"[^a-z0-9_]", "_", ascii_value)
    safe = re.sub(r"_+", "_", safe).strip("_")
    return safe or "value"


def build_emotion_column_map(emotions: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    used: set[str] = set()
    for emotion in emotions:
        base = f"emotion_{sanitize_for_column(emotion)}"
        candidate = base
        suffix = 2
        while candidate in used:
            candidate = f"{base}_{suffix}"
            suffix += 1
        mapping[emotion] = candidate
        used.add(candidate)
    return mapping


def init_state() -> None:
    defaults = {
        "phase": "setup",
        "name": "",
        "test_option": "emotions",
        "selected_emotions": [],
        "images": [],
        "current_index": 0,
        "ratings": {},
        "saved_csv_path": "",
        "saved_rows": 0,
        "finish_confirm_visible": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def start_session(
    name: str, test_option: str, selected_emotions: list[str], images: list[Path]
) -> None:
    st.session_state.phase = "rating"
    st.session_state.name = name
    st.session_state.test_option = test_option
    st.session_state.selected_emotions = selected_emotions
    st.session_state.images = [str(path) for path in images]
    st.session_state.current_index = 0
    st.session_state.ratings = {}
    st.session_state.saved_csv_path = ""
    st.session_state.saved_rows = 0
    st.session_state.finish_confirm_visible = False
    st.rerun()


def build_results_dataframe() -> pd.DataFrame:
    test_option = st.session_state.test_option
    selected_emotions = st.session_state.selected_emotions
    images = [Path(path) for path in st.session_state.images]
    ratings = st.session_state.ratings

    rows: list[dict[str, object]] = []
    emotion_column_map = (
        build_emotion_column_map(selected_emotions) if test_option == "emotions" else {}
    )

    for image_path in images:
        image_name = image_path.name
        if image_name not in ratings:
            continue

        record = ratings[image_name]
        row: dict[str, object] = {
            "name": st.session_state.name,
            "test_option": test_option,
            "selected_emotions": ";".join(selected_emotions)
            if test_option == "emotions"
            else "",
            "image_name": image_name,
        }

        if test_option == "emotions":
            values: dict[str, int] = record.get("emotion_values", {})
            for emotion, column_name in emotion_column_map.items():
                row[column_name] = values.get(emotion)
        else:
            row["quality_score"] = record.get("quality_score", "")
            row["comment"] = record.get("comment", "")

        rows.append(row)

    columns = ["name", "test_option", "selected_emotions", "image_name"]
    if test_option == "emotions":
        columns.extend(emotion_column_map[emotion] for emotion in selected_emotions)
    else:
        columns.extend(["quality_score", "comment"])

    return pd.DataFrame(rows, columns=columns)


def save_results_csv() -> None:
    ensure_dirs()
    dataframe = build_results_dataframe()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = sanitize_for_filename(st.session_state.name)
    output_path = OUTPUT_DIR / f"results_{timestamp}_{safe_name}.csv"
    dataframe.to_csv(output_path, index=False, encoding="utf-8-sig")

    st.session_state.phase = "finished"
    st.session_state.saved_csv_path = str(output_path)
    st.session_state.saved_rows = len(dataframe)
    st.session_state.finish_confirm_visible = False


def request_finish_confirmation() -> None:
    st.session_state.finish_confirm_visible = True
    st.rerun()


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


def reset_session() -> None:
    st.session_state.clear()
    st.rerun()


def format_quality_option(value: str) -> str:
    labels = {
        "1": "1 (good image)",
        "0.5": "0.5 (partially good image)",
        "0": "0 (reject image)",
    }
    return labels.get(value, value)


def render_setup_screen() -> None:
    st.title("Local image rating app")

    image_paths = get_image_paths()
    if not image_paths:
        st.warning("No images found in new_images")

    st.text_input("Name", key="draft_name")
    selected_option_label = st.radio(
        "Choose test",
        options=[OPTION_QUALITY_LABEL, OPTION_EMOTIONS_LABEL],
        key="draft_option",
    )

    selected_emotions: list[str] = []
    if selected_option_label == OPTION_EMOTIONS_LABEL:
        st.write("Choose emotions:")
        for idx, emotion in enumerate(DEFAULT_EMOTIONS):
            if st.checkbox(emotion, value=True, key=f"draft_emotion_{idx}"):
                selected_emotions.append(emotion)

    start_disabled = len(image_paths) == 0
    if st.button("Start", type="primary", disabled=start_disabled):
        errors: list[str] = []
        user_name = st.session_state.get("draft_name", "").strip()
        test_option = (
            "emotions"
            if selected_option_label == OPTION_EMOTIONS_LABEL
            else "quality"
        )

        if not user_name:
            errors.append("Name is required.")
        if test_option == "emotions" and not selected_emotions:
            errors.append("Select at least one emotion.")
        if not image_paths:
            errors.append("No images found in new_images.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            start_session(user_name, test_option, selected_emotions, image_paths)


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


def hydrate_form_state_from_saved_rating(current_path: Path, current_index: int) -> None:
    image_name = current_path.name
    saved_record = st.session_state.ratings.get(image_name, {})

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
        st.warning("No images to rate. Return to the start screen.")
        if st.button("New session"):
            reset_session()
        return

    current_index = st.session_state.current_index
    if st.session_state.finish_confirm_visible:
        render_finish_confirmation_dialog()

    if current_index >= total:
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
        st.subheader(f"Image {current_index + 1} of {total}")
        st.caption(f"File name: `{current_path.name}`")
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
                "<div style='margin: 0 0 0.45rem 0;'>Emotion rating (1-7):</div>",
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
            previous_clicked = st.button("Previous", disabled=current_index == 0)
        with col_next:
            next_clicked = st.button("Next", type="primary")

    if previous_clicked:
        st.session_state.finish_confirm_visible = False
        if current_index > 0:
            st.session_state.current_index = current_index - 1
        st.rerun()

    if next_clicked:
        st.session_state.finish_confirm_visible = False
        if not is_valid:
            st.error(error_message)
        else:
            if st.session_state.test_option == "emotions":
                st.session_state.ratings[current_path.name] = {
                    "emotion_values": payload,
                }
            else:
                st.session_state.ratings[current_path.name] = {
                    "quality_score": payload["quality_score"],
                    "comment": payload["comment"],
                }
            st.session_state.current_index = current_index + 1
            st.rerun()

    if finish_clicked:
        request_finish_confirmation()


def render_finished_screen() -> None:
    st.success("Results saved.")
    st.write(f"Number of saved ratings: {st.session_state.saved_rows}")
    st.write(f"CSV file: `{st.session_state.saved_csv_path}`")
    if st.button("New session", type="primary"):
        reset_session()


def main() -> None:
    st.set_page_config(page_title="Image rating", layout="wide")
    inject_custom_button_styles()
    ensure_dirs()
    init_state()

    phase = st.session_state.phase
    if phase == "setup":
        render_setup_screen()
    elif phase == "rating":
        render_rating_screen()
    elif phase == "finished":
        render_finished_screen()
    else:
        reset_session()


if __name__ == "__main__":
    main()
