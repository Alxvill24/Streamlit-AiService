import streamlit as st
import google.generativeai as genai

# CONFIGURAR API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# ESTILOS
st.markdown("""
    <style>
        body { background-color: #ffffff; }

        .title {
            color: #5b2e91;
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 25px;
        }

        /* CONTENEDOR INPUT ARRIBA */
        .input-block {
            padding: 20px;
            background-color: #faf7ff;
            border: 2px solid #5b2e91;
            border-radius: 14px;
            margin-bottom: 25px;
        }

        /* textarea */
        textarea {
            border-radius: 8px !important;
            border: 2px solid #5b2e91 !important;
            background-color: #ffffff !important;
            color: #2e2e2e !important;
        }

        /* botón */
        .send-btn button {
            background-color: #5b2e91 !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 6px 12px !important;
            border: 2px solid #ffda55 !important;
            margin-top: 8px;
        }

        .send-btn button:hover {
            background-color: #43206d !important;
        }

        /* BLOQUES DE RESPUESTA TIPO GPT */
        .response-block {
            background-color: #f3eaff;
            border-left: 6px solid #5b2e91;
            padding: 24px;
            margin-bottom: 18px;
            border-radius: 10px;
            font-size: 17px;
            line-height: 1.6;
            color: #2e2e2e;
        }

        .user-block {
            background-color: #fff;
            border-left: 6px solid #ffda55;
            padding: 24px;
            margin-bottom: 18px;
            border-radius: 10px;
            font-size: 17px;
            color: #2e2e2e;
        }
    </style>
""", unsafe_allow_html=True)

# TÍTULO
st.markdown("<h1 class='title'>Gemini WebApp</h1>", unsafe_allow_html=True)

# -------- ENTRADA ARRIBA --------
st.markdown("<div class='input-block'>", unsafe_allow_html=True)

prompt = st.text_area("Escribe tu prompt:", label_visibility="collapsed")

col1, col2 = st.columns([7,1])
with col2:
    send = st.button("Enviar", key="send_btn")

st.markdown("</div>", unsafe_allow_html=True)

# -------- HISTORIAL DE BLOQUES --------
if "history" not in st.session_state:
    st.session_state.history = []

if send and prompt.strip():
    # Guardar el bloque del usuario
    st.session_state.history.append({
        "role": "user",
        "text": prompt
    })

    # Obtener respuesta
    res = model.generate_content(prompt)
    st.session_state.history.append({
        "role": "ai",
        "text": res.text
    })

# Mostrar como bloques tipo GPT
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='user-block'>{msg['text']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='response-block'>{msg['text']}</div>",
            unsafe_allow_html=True
        )
