import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Chat Gemini 2.5 Flash", layout="centered")

# --- Configuración de API ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# --- CSS personalizado ---
st.markdown("""
<style>

    body {
        background-color: #ffffff;
    }

    /* Caja de texto */
    textarea {
        border-radius: 10px !important;
        border: 2px solid #6A1B9A !important;
        padding: 10px !important;
        font-size: 16px !important;
    }

    /* Botón pequeño */
    .small-button button {
        background-color: #6A1B9A;
        color: white;
        border-radius: 6px;
        padding: 6px 12px;
        border: none;
        font-size: 13px;
    }
    .small-button button:hover {
        background-color: #4a0f6d;
    }

    /* Output box */
    .output-box {
        background: #f8f3fc;
        border-left: 4px solid #FFC400;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        border: 1px solid #e5d7f3;
    }

</style>
""", unsafe_allow_html=True)


# --- JavaScript para Enter = enviar y Shift+Enter = nueva línea ---
enter_script = """
<script>
document.addEventListener("keydown", function(event) {
    let textarea = document.querySelector("textarea");
    if (!textarea) return;

    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        const streamlitSendButton = window.parent.document.querySelector('button[kind="primary"]');
        if (streamlitSendButton) streamlitSendButton.click();
    }
});
</script>
"""

st.markdown(enter_script, unsafe_allow_html=True)

# --- UI MAIN ---
st.header("Chat con Gemini 2.5 Flash")

# Input + botón en columnas
col1, col2 = st.columns([8, 1])

with col1:
    prompt = st.text_area("Escribe tu prompt:", height=120, label_visibility="collapsed")

with col2:
    send = st.button("Enviar", key="send_button", help="Enviar prompt", type="primary")

# Envío cuando Enter o botón
if send and prompt.strip() != "":
    with st.spinner("Generando respuesta..."):
        try:
            response = model.generate_content(prompt)
            st.markdown(f"<div class='output-box'>{response.text}</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")
