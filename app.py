import streamlit as st
import google.generativeai as genai

# Configurar Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# ----- ESTILOS -----
st.markdown("""
    <style>

        body {
            background-color: #ffffff;
        }

        /* Título */
        .title {
            color: #5b2e91;
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 20px;
        }

        /* Bloque estilo GPT — usuario */
        .user-block {
            background-color: rgba(250, 245, 255, 0.7);
            border-left: 6px solid #ffda55;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 18px;
            font-size: 17px;
            line-height: 1.6;
            color: #222;
        }

        /* Bloque estilo GPT — modelo */
        .ai-block {
            background-color: rgba(243, 234, 255, 0.85);
            border-left: 6px solid #5b2e91;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 18px;
            font-size: 17px;
            line-height: 1.6;
            color: #222;
        }

        /* Caja input flotante abajo */
        .input-floating {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 15px;
            background-color: #faf5ff;
            border-top: 3px solid #5b2e91;
            z-index: 10000;
        }

        textarea {
            background-color: #ffffff !important;
            border-radius: 10px !important;
            border: 2px solid #5b2e91 !important;
            color: #222 !important;
            font-size: 16px !important;
        }

        .send-btn button {
            background-color: #5b2e91 !important;
            color: white !important;
            border-radius: 8px !important;
            border: 2px solid #ffda55 !important;
            padding: 6px 12px !important;
            margin-top: 8px;
        }

    </style>
""", unsafe_allow_html=True)


# ----- TITULO -----
st.markdown("<h1 class='title'>Gemini WebApp</h1>", unsafe_allow_html=True)


# ----- HISTORIAL -----
if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-block'>{msg['text']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai-block'>{msg['text']}</div>", unsafe_allow_html=True)


# ----- INPUT ABAJO -----
st.markdown("<div class='input-floating'>", unsafe_allow_html=True)

# Estado temporal del input
if "current_input" not in st.session_state:
    st.session_state.current_input = ""

prompt = st.text_area(
    "Escribe tu prompt:",
    value=st.session_state.current_input,
    key="prompt_text",
    label_visibility="collapsed"
)

send = st.button("Enviar", key="send_btn")

st.markdown("</div>", unsafe_allow_html=True)


# ----- LÓGICA -----
if send and prompt.strip():
    st.session_state.history.append({"role": "user", "text": prompt})

    result = model.generate_content(prompt)
    st.session_state.history.append({"role": "ai", "text": result.text})

    # LIMPIEZA CORRECTA (FIX)
    st.session_state.current_input = ""
    st.session_state["prompt_text"] = ""   # <-- CORREGIDO
    st.rerun()


# ----- JS PARA ENTER Y CTRL+ENTER -----
st.markdown("""
<script>
document.addEventListener("keydown", function(e) {
    const textarea = document.querySelector("textarea");
    if (!textarea) return;

    // Ctrl+Enter: salto de línea
    if (e.key === "Enter" && e.ctrlKey) {
        e.preventDefault();
        textarea.value += "\\n";
        textarea.dispatchEvent(new Event("input", { bubbles: true }));
        return;
    }

    // Enter: enviar
    if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey) {
        e.preventDefault();
        const sendBtn = window.parent.document.querySelector('button[kind="primary"]');
        if (sendBtn) sendBtn.click();
    }
});
</script>
""", unsafe_allow_html=True)
