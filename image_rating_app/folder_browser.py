import os
from pathlib import Path

import streamlit as st


def validate_folder(value: str) -> Path:
    value = value.strip().strip('"')
    if not value:
        raise ValueError("Enter a folder path.")
    folder = Path(os.path.expandvars(value)).expanduser().resolve(strict=True)
    if not folder.is_dir():
        raise NotADirectoryError("Choose a folder, rather than an image file.")
    # Check access before accepting a folder, including an empty one.
    with os.scandir(folder):
        pass
    return folder


def list_subfolders(folder: Path) -> list[Path]:
    return sorted((path for path in folder.iterdir() if path.is_dir()), key=lambda p: p.name.casefold())


def get_browse_locations() -> dict[str, Path]:
    home = Path.home()
    locations = {"Home": home}
    for name in ("Desktop", "Documents", "Downloads"):
        if (home / name).is_dir():
            locations[name] = home / name
    if os.name == "nt":
        import ctypes

        drives = ctypes.windll.kernel32.GetLogicalDrives()
        for index in range(26):
            if drives & (1 << index):
                letter = chr(ord("A") + index)
                locations[f"Drive {letter}:"] = Path(f"{letter}:/")
    else:
        locations["Computer /"] = Path("/")
    return locations


def _navigate_to_folder(value: str) -> None:
    try:
        folder = validate_folder(value)
    except (OSError, ValueError) as error:
        st.session_state.folder_browser_error = f"Cannot open this folder: {error}"
        return
    st.session_state.folder_browser_current = str(folder)
    st.session_state.folder_browser_address = str(folder)
    st.session_state.folder_browser_location = None
    st.session_state.folder_browser_child = None
    st.session_state.folder_browser_error = ""


def open_folder_browser(initial_folder: Path) -> None:
    try:
        initial = validate_folder(str(initial_folder))
    except (OSError, ValueError):
        initial = Path.home()
    _navigate_to_folder(str(initial))
    st.session_state.folder_browser_visible = True


def _go_to_address() -> None:
    _navigate_to_folder(st.session_state.folder_browser_address)


def _jump_to_location() -> None:
    location = st.session_state.folder_browser_location
    if location:
        _navigate_to_folder(str(get_browse_locations()[location]))


def _close_folder_browser() -> None:
    st.session_state.folder_browser_visible = False


def _use_current_folder() -> None:
    try:
        folder = validate_folder(st.session_state.folder_browser_current)
    except (OSError, ValueError) as error:
        st.session_state.folder_browser_error = f"Cannot use this folder: {error}"
        return
    st.session_state.source_image_root = str(folder)
    st.session_state.draft_image_folder = None
    _close_folder_browser()


def use_default_image_folder() -> None:
    st.session_state.source_image_root = ""
    st.session_state.draft_image_folder = None


@st.dialog("Choose an image folder", width="large", on_dismiss=_close_folder_browser)
def render_folder_browser() -> None:
    if not st.session_state.folder_browser_visible:
        st.rerun()

    locations = get_browse_locations()
    st.selectbox(
        "Jump to", [None, *locations],
        format_func=lambda name: "Choose a drive or location" if name is None else name,
        key="folder_browser_location", on_change=_jump_to_location,
    )
    address_col, go_col = st.columns([5, 1], vertical_alignment="bottom")
    with address_col:
        st.text_input("Folder path", key="folder_browser_address", on_change=_go_to_address)
    with go_col:
        st.button("Go", key="folder_browser_go", on_click=_go_to_address, width="stretch")

    current = Path(st.session_state.folder_browser_current)
    st.caption(f"Browsing: {current}")
    st.button(
        "↑ Parent folder", key="folder_browser_up",
        on_click=_navigate_to_folder, args=(str(current.parent),), disabled=current == current.parent,
    )
    try:
        subfolders = list_subfolders(current)
    except OSError as error:
        subfolders = []
        st.session_state.folder_browser_error = f"Cannot list this folder: {error}"

    names = [path.name for path in subfolders]
    if st.session_state.get("folder_browser_child") not in names:
        st.session_state.folder_browser_child = None
    folder_col, open_col = st.columns([5, 1], vertical_alignment="bottom")
    with folder_col:
        selected = st.selectbox("Subfolders", names, index=None, key="folder_browser_child", placeholder="Select a folder to open")
    with open_col:
        st.button(
            "Open", key="folder_browser_open", width="stretch", disabled=selected is None,
            on_click=_navigate_to_folder, args=(str(current / selected) if selected else str(current),),
        )
    if not subfolders:
        st.caption("No subfolders here. You can choose this folder to use its images.")
    error = st.session_state.get("folder_browser_error", "")
    if error:
        st.error(error)
    choose_col, cancel_col = st.columns(2)
    with choose_col:
        st.button("Use this folder", key="folder_browser_use", type="primary", width="stretch", disabled=bool(error), on_click=_use_current_folder)
    with cancel_col:
        st.button("Cancel", key="folder_browser_cancel", width="stretch", on_click=_close_folder_browser)
