import streamlit as st
import streamlit.components.v1 as components


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
            max-width: 1700px !important;
            margin-left: auto !important;
            margin-right: auto !important;
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
