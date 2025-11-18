import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="GPT Style Chat", layout="centered")

# Global CSS for black font
st.markdown(
    """
    <style>
        * { color: black !important; }
        textarea, input, .stMarkdown, .stChatMessage, .stTextInput { color: black !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

if "user_input_js" not in st.session_state:
    st.session_state.user_input_js = ""

# Title
st.markdown("<h2 style='color:black'>Chat estilo GPT</h2>", unsafe_allow_html=True)

# Inject JavaScript for Enter (send) / Shift+Enter (newline)
html(
    """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const textarea = window.parent.document.querySelector('textarea[data-testid="stTextArea"]');
        if (!textarea) return;

        textarea.addEventListener('keydown', function(e){
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const text = textarea.value;
                textarea.value = "";

                window.parent.postMessage({
                    isStreamlitMessage: true,
                    type: "SET_COMPONENT_VALUE",
                    key: "user_input_js",
                    value: text
                }, "*");
            }
        });
    });
    </script>
    """,
    height=0,
)

# Display chat history
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"<div style='background:#e6e6e6;border-radius:10px;padding:10px;margin:5px 0;color:black'><b>Tú:</b> {msg['text']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background:#dcdcdc;border-radius:10px;padding:10px;margin:5px 0;color:black'><b>AI:</b> {msg['text']}</div>", unsafe_allow_html=True)

# Text input area
user_text = st.text_area(
    "Mensaje:",
    key="user_input",
    placeholder="Escribe algo... (Enter para enviar / Shift+Enter para salto de línea)",
    height=100,
)

# If JS sent text
if st.session_state.user_input_js:
    text = st.session_state.user_input_js
    st.session_state.user_input_js = ""

    st.session_state.history.append({"role": "user", "text": text})

    # Placeholder AI response
    ai_response = f"Procesé tu mensaje: {text}"
    st.session_state.history.append({"role": "ai", "text": ai_response})

    st.experimental_rerun()
