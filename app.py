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
            margin-bottom: 25px;
        }

        /* Contenedor del input */
        .input-wrapper {
            background-color: #faf5ff;
            border: 2px solid #5b2e91;
            border-radius: 14px;
            padding: 18px;
            margin-bottom: 25px;
        }

        /* Textarea */
        textarea {
            background-color: #ffffff !important;
            border-radius: 10px !important;
            border: 2px solid #5b2e91 !important;
            color: #222 !important;
            font-size: 16px !important;
        }

        /* Botón */
        .send-btn button {
            background-color: #5b2e91 !important;
            color: white !important;
            border-radius: 8px !important;
            border: 2px solid #ffda55 !important;
            padding: 6px 12px !important;
        }
        .send-btn button:hover {
            background-color: #43206d !important;
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

    </style>
""", unsafe_allow_html=True)

# Título
st.markdown("<h1 class='title'>Gemini WebApp</h1>", unsafe_allow_html=True)

# -------- INPUT SIEMPRE ARRIBA --------
st.markdown("<div class='input-wrapper'>", unsafe_allow_html=True)

prompt = st.text_area("Escribe tu prompt:", label_visibility="collapsed")

col1, col2 = st.columns([7,1])
with col2:
    send = st.button("Enviar", key="send_btn")

st.markdown("</div>", unsafe_allow_html=True)

# -------- HISTORIAL --------
if "history" not in st.session_state:
    st.session_state.history = []

if send and prompt.strip():
    st.session_state.history.append({"role": "user", "text": prompt})

    result = model.generate_content(prompt)
    st.session_state.history.append({"role": "ai", "text": result.text})

# -------- MOSTRAR BLOQUES --------
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-block'>{msg['text']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai-block'>{msg['text']}</div>", unsafe_allow_html=True)
