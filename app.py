import streamlit as st
import google.generativeai as genai

# --- Configuración inicial ---
st.set_page_config(page_title="Chat con Gemini", page_icon="✨", layout="centered")

# Cargar API key desde Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Modelo a usar
model = genai.GenerativeModel("gemini-2.5-flash")

# --- CSS Personalizado ---
st.markdown("""
<style>
body {
    background: #f5f7fa;
}
textarea, input {
    border-radius: 10px !important;
}
div.stButton > button {
    background-color: #4a90e2;
    color: white;
    padding: 0.6rem 1.2rem;
    border-radius: 10px;
    border: none;
    font-size: 16px;
}
div.stButton > button:hover {
    background-color: #357ABD;
}
.output-box {
    background: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #ddd;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# --- Título ---
st.title("✨ WebApp con Streamlit + Gemini")

# --- Entrada de prompt ---
prompt = st.text_area("Escribe tu prompt:", height=150)

# --- Botón para enviar petición ---
if st.button("Enviar a Gemini"):
    if prompt.strip() == "":
        st.warning("Por favor escribe algo antes de enviar.")
    else:
        with st.spinner("Generando respuesta..."):
            try:
                # Llamada HTTP al modelo
                response = model.generate_content(prompt)

                # Mostrar salida
                st.markdown(f"<div class='output-box'>{response.text}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")
