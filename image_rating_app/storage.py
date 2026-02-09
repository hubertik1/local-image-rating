from datetime import datetime
from pathlib import Path
import re
import unicodedata

import pandas as pd
import streamlit as st

from .constants import IMAGE_DIR, OUTPUT_DIR, SUPPORTED_EXTENSIONS


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
