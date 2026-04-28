from datetime import datetime
from pathlib import Path
import re
import unicodedata

import pandas as pd
import streamlit as st

from .constants import (
    IMAGE_DIR,
    OUTPUT_DIR,
    SUPPORTED_EXTENSIONS,
    TEST_OPTION_EMOTIONS,
    TEST_OPTION_TRIPLET_QUALITY,
    TRIPLET_IMAGE_COUNT,
)


TRIPLET_MEMBER_PATTERN = re.compile(r"^(?P<base>.+)_(?P<slot>[123])$")


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


def parse_triplet_member(image_path: Path) -> tuple[str, int] | None:
    match = TRIPLET_MEMBER_PATTERN.match(image_path.stem)
    if match is None:
        return None

    try:
        relative_path = image_path.relative_to(IMAGE_DIR)
    except ValueError:
        relative_path = image_path

    group_path = relative_path.with_name(match.group("base"))
    return group_path.as_posix(), int(match.group("slot"))


def build_triplet_image_groups(
    image_paths: list[Path],
) -> tuple[list[list[Path]], list[str]]:
    grouped_paths: dict[str, dict[int, Path]] = {}

    for image_path in image_paths:
        parsed = parse_triplet_member(image_path)
        if parsed is None:
            continue

        group_key, slot = parsed
        grouped_paths.setdefault(group_key, {})
        grouped_paths[group_key].setdefault(slot, image_path)

    image_groups: list[list[Path]] = []
    incomplete_group_keys: list[str] = []
    for group_key in sorted(grouped_paths):
        slot_map = grouped_paths[group_key]
        ordered_group = [
            slot_map[slot]
            for slot in range(1, TRIPLET_IMAGE_COUNT + 1)
            if slot in slot_map
        ]
        image_groups.append(ordered_group)
        if len(ordered_group) < TRIPLET_IMAGE_COUNT:
            incomplete_group_keys.append(group_key)

    return image_groups, incomplete_group_keys


def get_triplet_group_key(image_group: list[Path]) -> str:
    if not image_group:
        return ""

    parsed = parse_triplet_member(image_group[0])
    if parsed is not None:
        group_key, _ = parsed
        return group_key

    return "|".join(get_image_key(image_path) for image_path in image_group)


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
        base = sanitize_for_column(emotion)
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
    image_groups = [
        [Path(path) for path in group]
        for group in st.session_state.get("image_groups", [])
    ]
    ratings = st.session_state.ratings

    rows: list[dict[str, object]] = []
    emotion_column_map = (
        build_emotion_column_map(selected_emotions)
        if test_option == TEST_OPTION_EMOTIONS
        else {}
    )

    if test_option == TEST_OPTION_TRIPLET_QUALITY:
        for image_group in image_groups:
            group_key = get_triplet_group_key(image_group)
            if group_key not in ratings:
                continue

            record = ratings[group_key]
            items: list[dict[str, str]] = record.get("items", [])
            row: dict[str, object] = {
                "name": st.session_state.name,
                "test_option": test_option,
            }

            for idx in range(1, TRIPLET_IMAGE_COUNT + 1):
                row[f"image_name_{idx}"] = ""
                row[f"quality_score_{idx}"] = ""
                row[f"comment_{idx}"] = ""

            for item_index, image_path in enumerate(image_group):
                parsed = parse_triplet_member(image_path)
                idx = parsed[1] if parsed is not None else item_index + 1
                item = items[item_index] if item_index < len(items) else {}
                row[f"image_name_{idx}"] = image_path.name
                row[f"quality_score_{idx}"] = item.get("quality_score", "")
                row[f"comment_{idx}"] = item.get("comment", "")

            rows.append(row)

        columns = ["name", "test_option"]
        for idx in range(1, TRIPLET_IMAGE_COUNT + 1):
            columns.extend([f"image_name_{idx}", f"quality_score_{idx}", f"comment_{idx}"])
        return pd.DataFrame(rows, columns=columns)

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

        if test_option == TEST_OPTION_EMOTIONS:
            row["selected_emotions"] = ";".join(selected_emotions)
            values: dict[str, int] = record.get("emotion_values", {})
            for emotion, column_name in emotion_column_map.items():
                row[column_name] = values.get(emotion)
        else:
            row["quality_score"] = record.get("quality_score", "")
            row["comment"] = record.get("comment", "")

        rows.append(row)

    columns = ["name", "test_option", "image_name"]
    if test_option == TEST_OPTION_EMOTIONS:
        columns.insert(2, "selected_emotions")
        columns.extend(emotion_column_map[emotion] for emotion in selected_emotions)
    else:
        columns.extend(["quality_score", "comment"])

    return pd.DataFrame(rows, columns=columns)


def save_results_csv() -> None:
    ensure_dirs()
    dataframe = build_results_dataframe()
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    safe_name = sanitize_for_filename(st.session_state.name)
    output_path = OUTPUT_DIR / f"results_{timestamp}_{safe_name}.csv"
    dataframe.to_csv(output_path, index=False, encoding="utf-8-sig")

    st.session_state.phase = "finished"
    st.session_state.saved_csv_path = str(output_path)
    st.session_state.saved_rows = len(dataframe)
    st.session_state.finish_confirm_visible = False
