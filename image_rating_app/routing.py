import streamlit as st

from .constants import TEST_OPTION_BEST_OF_THREE, TEST_OPTION_TRIPLET_QUALITY


PAGE_SETUP = "setup"
PAGE_RATING = "rating"
PAGE_FINISHED = "finished"
VALID_PAGES = {PAGE_SETUP, PAGE_RATING, PAGE_FINISHED}


def _clear_transient_ui() -> None:
    st.session_state.finish_confirm_visible = False
    st.session_state.error_alert_message = ""


def _replace_query_params(params: dict[str, str]) -> None:
    current_params = {key: str(value) for key, value in st.query_params.items()}
    if current_params != params:
        st.query_params.from_dict(params)


def set_route(page: str, index: int | None = None) -> None:
    """Update the URL and matching in-memory navigation state."""
    if page not in VALID_PAGES:
        page = PAGE_SETUP

    _clear_transient_ui()
    st.session_state.phase = page
    params = {"page": page}

    if page == PAGE_RATING:
        safe_index = max(0, index if index is not None else 0)
        st.session_state.current_index = safe_index
        params["index"] = str(safe_index)

    _replace_query_params(params)


def navigate_to(page: str, index: int | None = None) -> None:
    set_route(page, index)
    st.rerun()


def _rating_item_count() -> int:
    if st.session_state.test_option in {
        TEST_OPTION_TRIPLET_QUALITY,
        TEST_OPTION_BEST_OF_THREE,
    }:
        return len(st.session_state.get("image_groups", []))
    return len(st.session_state.get("images", []))


def _parse_index(raw_index: object, maximum: int) -> int:
    try:
        index = int(str(raw_index))
    except (TypeError, ValueError):
        return 0
    return min(max(index, 0), maximum)


def apply_route_from_url() -> None:
    """Make browser Back/Forward navigation drive the rendered screen."""
    requested_page = str(st.query_params.get("page", PAGE_SETUP))
    previous_page = st.session_state.phase
    previous_index = st.session_state.current_index

    if requested_page not in VALID_PAGES:
        set_route(PAGE_SETUP)
        return

    if requested_page == PAGE_SETUP:
        if previous_page != PAGE_SETUP:
            _clear_transient_ui()
        st.session_state.phase = PAGE_SETUP
        if "page" in st.query_params:
            _replace_query_params({"page": PAGE_SETUP})
        return

    if requested_page == PAGE_RATING:
        item_count = _rating_item_count()
        if not st.session_state.get("name") or item_count == 0:
            set_route(PAGE_SETUP)
            return

        route_index = _parse_index(
            st.query_params.get("index", 0),
            item_count,
        )
        if previous_page != PAGE_RATING or previous_index != route_index:
            _clear_transient_ui()
        st.session_state.phase = PAGE_RATING
        st.session_state.current_index = route_index
        _replace_query_params(
            {"page": PAGE_RATING, "index": str(route_index)}
        )
        return

    if not st.session_state.get("saved_csv_path"):
        fallback_page = PAGE_RATING if _rating_item_count() else PAGE_SETUP
        fallback_index = st.session_state.get("current_index", 0)
        set_route(fallback_page, fallback_index)
        return

    if previous_page != PAGE_FINISHED:
        _clear_transient_ui()
    st.session_state.phase = PAGE_FINISHED
    _replace_query_params({"page": PAGE_FINISHED})
