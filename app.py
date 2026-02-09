from __future__ import annotations

from datetime import datetime
import html
from pathlib import Path
import re
import unicodedata

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

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
    "happiness",
    "suprise",
]
EMOTIONS_LEFT_COLUMN_COUNT = 12
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

        /* Fine alignment for Show labels beside File name */
        .st-key-rating_show_labels {
            position: relative !important;
            top: -0.rem !important;
        }
        .st-key-rating_show_labels [data-testid="stCheckbox"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def sync_keyboard_shortcuts(enabled: bool) -> None:
    enabled_js = "true" if enabled else "false"
    components.html(
        f"""
        <script>
        (() => {{
            const doc = window.parent.document;
            doc.__ratingHotkeysEnabled = {enabled_js};

            if (doc.__ratingHotkeysBound) {{
                return;
            }}
            doc.__ratingHotkeysBound = true;

            doc.addEventListener(
                "keydown",
                (event) => {{
                    if (!doc.__ratingHotkeysEnabled || event.repeat) {{
                        return;
                    }}

                    const active = doc.activeElement;
                    const tagName = active?.tagName?.toLowerCase?.() ?? "";
                    const inputType = active?.type?.toLowerCase?.() ?? "";
                    const isTypingField =
                        !!active &&
                        (active.isContentEditable ||
                            tagName === "textarea" ||
                            tagName === "select" ||
                            (tagName === "input" && !["radio", "checkbox"].includes(inputType)));
                    if (isTypingField) {{
                        return;
                    }}

                    let selector = "";
                    if (event.key === "ArrowLeft") {{
                        selector = ".st-key-previous_btn button:not([disabled])";
                    }} else if (event.key === "ArrowRight" || event.key === "Enter") {{
                        selector = ".st-key-next_btn button:not([disabled])";
                    }} else {{
                        return;
                    }}

                    const targetButton = doc.querySelector(selector);
                    if (!targetButton) {{
                        return;
                    }}

                    event.preventDefault();
                    event.stopPropagation();
                    targetButton.click();
                }},
                true
            );
        }})();
        </script>
        """,
        height=0,
    )


def ensure_dirs() -> None:
    IMAGE_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)


def get_image_paths() -> list[Path]:
    ensure_dirs()
    images = [
        path
        for path in IMAGE_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(images, key=lambda p: str(p.relative_to(IMAGE_DIR)).lower())


def get_image_key(image_path: Path) -> str:
    try:
        return image_path.relative_to(IMAGE_DIR).as_posix()
    except ValueError:
        return image_path.as_posix()


def get_image_label(image_path: Path) -> str:
    try:
        relative_path = image_path.relative_to(IMAGE_DIR)
    except ValueError:
        return ""

    if relative_path.parent == Path("."):
        return ""
    return relative_path.parent.name


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
        image_key = get_image_key(image_path)
        if image_key not in ratings:
            continue

        record = ratings[image_key]
        row: dict[str, object] = {
            "name": st.session_state.name,
            "test_option": test_option,
            "image_name": image_name,
        }

        if test_option == "emotions":
            row["selected_emotions"] = ";".join(selected_emotions)
            values: dict[str, int] = record.get("emotion_values", {})
            for emotion, column_name in emotion_column_map.items():
                row[column_name] = values.get(emotion)
        else:
            row["quality_score"] = record.get("quality_score", "")
            row["comment"] = record.get("comment", "")

        rows.append(row)

    columns = ["name", "test_option", "image_name"]
    if test_option == "emotions":
        columns.insert(2, "selected_emotions")
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


def render_finished_screen() -> None:
    sync_keyboard_shortcuts(False)
    st.markdown("<div style='padding-top: 0.8rem;'></div>", unsafe_allow_html=True)
    st.success("Results saved.")
    st.write(f"Number of saved ratings: {st.session_state.saved_rows}")
    st.write(f"CSV file: `{st.session_state.saved_csv_path}`")
    if st.button("New session", type="primary"):
        reset_session()


def main() -> None:
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


if __name__ == "__main__":
    main()
