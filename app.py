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
OPTION_EMOTIONS_LABEL = "Ocena na emocjach"
OPTION_QUALITY_LABEL = "Ocena jakości 1 / 0.5 / 0 + komentarz"


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


def reset_session() -> None:
    st.session_state.clear()
    st.rerun()


def format_quality_option(value: str) -> str:
    labels = {
        "": "-- wybierz ocenę --",
        "1": "1 (zdjęcie dobre)",
        "0.5": "0.5 (zdjęcie nie do końca dobre)",
        "0": "0 (zdjęcie do odrzucenia)",
    }
    return labels.get(value, value)


def render_setup_screen() -> None:
    st.title("Lokalna ocena obrazów")

    image_paths = get_image_paths()
    if not image_paths:
        st.warning("Brak obrazów w new_images")

    st.text_input("Imię", key="draft_name")
    selected_option_label = st.radio(
        "Wybór testu",
        options=[OPTION_QUALITY_LABEL, OPTION_EMOTIONS_LABEL],
        key="draft_option",
    )

    selected_emotions: list[str] = []
    if selected_option_label == OPTION_EMOTIONS_LABEL:
        st.write("Wybierz emocje:")
        for idx, emotion in enumerate(DEFAULT_EMOTIONS):
            if st.checkbox(emotion, value=True, key=f"draft_emotion_{idx}"):
                selected_emotions.append(emotion)

    start_disabled = len(image_paths) == 0
    if st.button("Rozpocznij", type="primary", disabled=start_disabled):
        errors: list[str] = []
        user_name = st.session_state.get("draft_name", "").strip()
        test_option = (
            "emotions"
            if selected_option_label == OPTION_EMOTIONS_LABEL
            else "quality"
        )

        if not user_name:
            errors.append("Imię jest wymagane.")
        if test_option == "emotions" and not selected_emotions:
            errors.append("Wybierz co najmniej jedną emocję.")
        if not image_paths:
            errors.append("Brak obrazów w new_images.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            start_session(user_name, test_option, selected_emotions, image_paths)


def render_emotions_form(current_index: int) -> tuple[bool, dict[str, int], str]:
    st.write("Ocena emocji (1-7):")
    selected_emotions: list[str] = st.session_state.selected_emotions
    values: dict[str, int] = {}

    for emotion_idx, emotion in enumerate(selected_emotions):
        key = f"emotion_score_{current_index}_{emotion_idx}"
        values[emotion] = st.slider(
            label=emotion,
            min_value=1,
            max_value=7,
            step=1,
            value=4,
            key=key,
        )

    is_valid = len(values) == len(selected_emotions)
    error = "" if is_valid else "Ustaw ocenę dla wszystkich emocji."
    return is_valid, values, error


def render_quality_form(current_index: int) -> tuple[bool, dict[str, str], str]:
    quality_score = st.selectbox(
        "Ocena jakości",
        options=["", "1", "0.5", "0"],
        format_func=format_quality_option,
        key=f"quality_score_{current_index}",
    )
    comment = st.text_area(
        "Komentarz (opcjonalnie)",
        key=f"quality_comment_{current_index}",
    )

    if quality_score == "":
        return False, {"quality_score": "", "comment": comment}, "Wybierz ocenę jakości."
    return True, {"quality_score": quality_score, "comment": comment}, ""


def render_rating_screen() -> None:
    images = [Path(path) for path in st.session_state.images]
    total = len(images)

    if total == 0:
        st.warning("Brak obrazów do oceny. Wróć do ekranu startowego.")
        if st.button("Nowa sesja"):
            reset_session()
        return

    current_index = st.session_state.current_index

    if current_index >= total:
        st.success("To już wszystkie obrazy")
        st.info(f"Ocenione obrazy: {len(st.session_state.ratings)} z {total}")
        if st.button("Zakończ i zapisz CSV", type="primary"):
            save_results_csv()
            st.rerun()
        return

    current_path = images[current_index]
    st.subheader(f"Obraz {current_index + 1} z {total}")
    st.caption(f"Nazwa pliku: `{current_path.name}`")

    if current_path.exists():
        st.image(str(current_path), use_container_width=True)
    else:
        st.error(f"Nie można wczytać obrazu: {current_path.name}")

    if st.session_state.test_option == "emotions":
        is_valid, payload, error_message = render_emotions_form(current_index)
    else:
        is_valid, payload, error_message = render_quality_form(current_index)

    col_next, col_finish = st.columns(2)
    with col_next:
        next_clicked = st.button("Next", type="primary")
    with col_finish:
        finish_clicked = st.button("Zakończ")

    if next_clicked:
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
        save_results_csv()
        st.rerun()


def render_finished_screen() -> None:
    st.success("Wyniki zostały zapisane.")
    st.write(f"Liczba zapisanych ocen: {st.session_state.saved_rows}")
    st.write(f"Plik CSV: `{st.session_state.saved_csv_path}`")
    if st.button("Nowa sesja", type="primary"):
        reset_session()


def main() -> None:
    st.set_page_config(page_title="Ocena obrazów", layout="wide")
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
