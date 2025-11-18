import streamlit as st
import google.generativeai as genai

# Configurar API Key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Crear cliente del modelo 2.5 Flash
model = genai.GenerativeModel("gemini-2.5-flash")

# --------- ESTILOS PERSONALIZADOS ----------
st.markdown("""
    <style>
        body {
            background-color: #ffffff;
        }

        .main {
            background-color: #ffffff;
        }

        /* Titulo */
        .title {
            color: #5b2e91;
            font-size: 32px;
            font-weight: 700;
        }

        /* Contenedor input y botón */
        .input-container {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 20px;
        }

        /* Caja de texto */
        .text-input textarea {
            border-radius: 8px !important;
            border: 2px solid #5b2e91 !important;
            background-color: #f9f5ff !important;
            color: #2d2d2d !important;
        }

        /* Botón enviar */
        .send-btn button {
            background-color: #5b2e91 !important;
            color: white !important;
            border-radius: 6px !important;
            padding: 6px 14px !important;
            border: 2px solid #ffda55 !important; /* acento amarillo */
        }

        .send-btn button:hover {
            background-color: #4a2375 !important;
        }

        /* Caja de salida */
        .output-box {
            margin-top: 25px;
            padding: 18px;
            border-radius: 12px;
            background-color: #f3eaff;
            border-left: 4px solid #5b2e91;
            color: #2e2e2e;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# --------- UI ---------

st.markdown("<h1 class='title'>Gemini WebApp</h1>", unsafe_allow_html=True)

# Entrada + botón a la derecha
st.markdown("<div class='input-container'>", unsafe_allow_html=True)

user_input = st.text_area(
    "Escribe tu prompt:",
    key="prompt",
    label_visibility="collapsed"
)

# Colocar botón a la derecha usando columnas invisibles
col1, col2 = st.columns([7, 1])
with col2:
    send = st.button("Enviar")

st.markdown("</div>", unsafe_allow_html=True)

# --------- LOGICA ---------
if send and user_input.strip():
    response = model.generate_content(user_input)
    st.markdown(
        f"<div class='output-box'>{response.text}</div>",
        unsafe_allow_html=True
    )
