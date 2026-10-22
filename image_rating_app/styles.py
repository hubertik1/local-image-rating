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

        /* Keep single-image reviews visible alongside their rating buttons. */
        .st-key-single_image_review_image [data-testid="stImage"] img {
            max-height: 70vh;
            object-fit: contain;
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
