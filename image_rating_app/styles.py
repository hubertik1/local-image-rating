import streamlit as st
import streamlit.components.v1 as components


def inject_custom_button_styles() -> None:
    st.markdown(
        """
        <style>
        /* Reduce top whitespace across all Streamlit views */
        [data-testid="stAppViewContainer"] > .main {
            padding-top: 0 !important;
        }
        .block-container {
            padding-top: 0.45rem !important;
            max-width: none !important;
            width: 100% !important;
            padding-left: clamp(1rem, 2vw, 3rem) !important;
            padding-right: clamp(1rem, 2vw, 3rem) !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }
        header[data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        .stDeployButton,
        #MainMenu {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
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

        /* Reserve the viewport for the image between two stationary bars. */
        .block-container:has(.st-key-single_image_review_header) {
            padding: 0 !important;
        }
        .st-key-single_image_review_header,
        .st-key-single_image_review_controls {
            position: fixed !important;
            left: 0.75rem !important;
            right: 0.75rem !important;
            width: auto !important;
            z-index: 20;
            box-sizing: border-box;
            background: var(--background-color, #ffffff);
            gap: 0.5rem !important;
        }
        .st-key-single_image_review_header {
            top: 0 !important;
            height: 64px !important;
            padding: 8px 0;
        }
        .st-key-single_image_review_controls {
            bottom: 0 !important;
            height: 128px !important;
            padding: 10px 0;
        }
        .st-key-single_image_review_header [data-testid="stHorizontalBlock"],
        .st-key-single_image_review_controls [data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            gap: 0.5rem !important;
        }
        .st-key-single_image_review_header [data-testid="stColumn"],
        .st-key-single_image_review_controls [data-testid="stColumn"] {
            min-width: 0 !important;
        }
        .st-key-single_image_review_header [data-testid="stVerticalBlock"],
        .st-key-single_image_review_controls [data-testid="stVerticalBlock"] {
            gap: 0.15rem !important;
        }
        .st-key-single_image_review_header h3 {
            font-size: 1.15rem !important;
            line-height: 1.3 !important;
            padding: 0 !important;
        }
        .st-key-single_image_review_header [data-testid="stMarkdownContainer"],
        .st-key-single_image_review_header [data-testid="stCaptionContainer"],
        .st-key-single_image_review_controls [data-testid="stCaptionContainer"] {
            margin: 0 !important;
        }
        .st-key-single_image_review_header [data-testid="stCaptionContainer"] p,
        .st-key-single_image_review_controls [data-testid="stCaptionContainer"] p {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin: 0;
            line-height: 18px;
        }
        .st-key-single_image_review_image {
            position: fixed !important;
            inset: 72px 0.75rem 136px !important;
            width: auto !important;
            height: auto !important;
        }
        .st-key-single_image_review_image [data-testid="stElementContainer"],
        .st-key-single_image_review_image [data-testid="stFullScreenFrame"],
        .st-key-single_image_review_image [data-testid="stFullScreenFrame"] > div,
        .st-key-single_image_review_image [data-testid="stImage"],
        .st-key-single_image_review_image [data-testid="stImageContainer"],
        .st-key-single_image_review_image [data-testid="stImage"] img {
            width: 100% !important;
            height: 100% !important;
            max-height: none !important;
        }
        .st-key-single_image_review_image [data-testid="stImage"] img {
            object-fit: contain;
        }
        div[class*="st-key-single_review_choice_"] button {
            height: 58px !important;
            min-height: 58px !important;
            border: 2px solid transparent !important;
            padding: 4px 8px !important;
            font-weight: 600;
        }
        .st-key-single_review_choice_great button {
            background: #15803d !important;
            color: #ffffff !important;
        }
        .st-key-single_review_choice_improve button {
            background: #facc15 !important;
            color: #422006 !important;
        }
        .st-key-single_review_choice_delete button {
            background: #dc2626 !important;
            color: #ffffff !important;
        }
        div[class*="st-key-single_review_choice_"] button:hover:not(:disabled) {
            filter: brightness(0.9);
        }
        div[class*="st-key-single_review_choice_"] button:disabled {
            opacity: 0.45;
        }
        div[class*="st-key-single_review_choice_"] button[data-testid="stBaseButton-primary"],
        div[class*="st-key-single_review_choice_"] button:focus-visible {
            outline: 3px solid #2563eb !important;
            outline-offset: 2px;
        }
        @media (max-width: 640px) {
            .st-key-single_image_review_header [data-testid="stColumn"],
            .st-key-single_image_review_controls [data-testid="stColumn"] {
                flex-basis: 0 !important;
            }
            .st-key-single_image_review_header h3 {
                font-size: 0.9rem !important;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .st-key-single_image_review_controls > [data-testid="stHorizontalBlock"]:first-child > [data-testid="stColumn"]:nth-child(2) {
                flex-grow: 1.7 !important;
            }
            .st-key-single_image_review_header button p,
            .st-key-single_image_review_controls button p {
                font-size: 0.8rem !important;
                line-height: 1.1 !important;
            }
        }

        /* Make best-of-three images clickable without a visible button. */
        div[class*="st-key-clickable_image_"] {
            position: relative !important;
        }
        div[class*="st-key-clickable_image_"]
        div[data-testid="stElementContainer"]:has(.stButton) {
            position: absolute !important;
            inset: 0 !important;
            width: 100% !important;
            height: 100% !important;
            z-index: 5 !important;
        }
        div[class*="st-key-clickable_image_"] .stButton,
        div[class*="st-key-clickable_image_"] .stButton button {
            width: 100% !important;
            height: 100% !important;
            margin: 0 !important;
        }
        div[class*="st-key-clickable_image_"] .stButton button {
            opacity: 0 !important;
            cursor: pointer !important;
        }
        div[class*="st-key-clickable_image_"]:has(.stButton button:hover)
        [data-testid="stImage"] {
            opacity: 0.86;
        }
        div[class*="st-key-clickable_image_selected_"] [data-testid="stImage"] {
            outline: 4px solid #1d4ed8;
            outline-offset: -4px;
            border-radius: 0.5rem;
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
            // Disable the legacy custom 1/2/3 handler after a hot reload.
            doc.__imageChoiceHotkeysEnabled = false;

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
                    const target = event.target;
                    const tagName = active?.tagName?.toLowerCase?.() ?? "";
                    const inputType = active?.type?.toLowerCase?.() ?? "";
                    const activeRole = active?.getAttribute?.("role") ?? "";
                    const isTypingField =
                        !!active &&
                        (active.isContentEditable ||
                            tagName === "textarea" ||
                            tagName === "select" ||
                            (tagName === "input" && !["radio", "checkbox"].includes(inputType)));
                    if (isTypingField) {{
                        return;
                    }}

                    const isInsideRadioUi = (element) =>
                        !!element &&
                        (
                            !!element.closest?.('div[role="radiogroup"]') ||
                            !!element.closest?.('[data-testid="stRadio"]')
                        );

                    const targetTag = target?.tagName?.toLowerCase?.() ?? "";
                    const targetType = target?.type?.toLowerCase?.() ?? "";
                    const targetRole = target?.getAttribute?.("role") ?? "";
                    const isRadioInteraction =
                        (tagName === "input" && inputType === "radio") ||
                        activeRole === "radio" ||
                        (targetTag === "input" && targetType === "radio") ||
                        targetRole === "radio" ||
                        isInsideRadioUi(active) ||
                        isInsideRadioUi(target);

                    if ((event.key === "ArrowUp" || event.key === "ArrowDown") && isRadioInteraction) {{
                        event.preventDefault();
                        event.stopPropagation();
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

                    event.preventDefault();
                    event.stopPropagation();

                    const targetButton = doc.querySelector(selector);
                    if (!targetButton) {{
                        return;
                    }}

                    targetButton.click();
                }},
                true
            );
        }})();
        </script>
        """,
        height=0,
    )
