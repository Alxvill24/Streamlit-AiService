import streamlit as st
import google.generativeai as genai
from datetime import datetime

# ------------------------------
# Config & API
# ------------------------------
st.set_page_config(page_title="Chat Gemini 2.5 Flash", layout="wide")
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
MODEL_NAME = "gemini-2.5-flash"

# ------------------------------
# Session state init
# ------------------------------
if "messages" not in st.session_state:
    # messages: list of dict {role: "user"/"assistant", "text": str, "time": str}
    st.session_state.messages = []

if "dark" not in st.session_state:
    st.session_state.dark = False

if "prompt" not in st.session_state:
    st.session_state.prompt = ""

# ------------------------------
# Theme colors
# ------------------------------
PURPLE = "#6A1B9A"
PURPLE_DARK = "#4a0f6d"
YELLOW = "#FFC400"
BG_LIGHT = "#ffffff"
BG_DARK = "#120417"
CARD_LIGHT = "#f8f3fc"
CARD_DARK = "#1b0d1b"

# ------------------------------
# CSS (light & dark) + layout tweaks
# ------------------------------
css = f"""
<style>
/* Base page */
.reportview-container .main {{
  background: {BG_LIGHT if not st.session_state.dark else BG_DARK};
}}
section.main > div {{
  max-width: 1200px;
  margin: 0 auto;
}}

/* Header */
.header-title {{
  font-size: 24px;
  font-weight: 600;
  color: {PURPLE if not st.session_state.dark else '#f6ecff'};
  margin-bottom: 6px;
}}

/* Chat column */
.chat-container {{
  padding: 18px;
  border-radius: 12px;
  background: {CARD_LIGHT if not st.session_state.dark else CARD_DARK};
  border: 1px solid rgba(106,27,154,0.06);
  height: 70vh;
  overflow-y: auto;
}}

/* Message bubbles */
.msg-user {{
  background: linear-gradient(90deg, {PURPLE} 0%, {PURPLE_DARK} 100%);
  color: white;
  padding: 10px 14px;
  border-radius: 14px;
  max-width: 78%;
  margin-left: auto;
  margin-bottom: 12px;
  box-shadow: 0 4px 10px rgba(106,27,154,0.12);
  font-size: 14px;
  white-space: pre-wrap;
}}
.msg-bot {{
  background: {BG_LIGHT if not st.session_state.dark else '#240726'};
  color: #111;
  padding: 10px 14px;
  border-radius: 14px;
  max-width: 78%;
  margin-right: auto;
  margin-bottom: 12px;
  border: 1px solid rgba(106,27,154,0.06);
  font-size: 14px;
  white-space: pre-wrap;
}}

/* Meta line */
.msg-meta {{
  font-size: 11px;
  color: #666;
  margin-top: 4px;
}}

/* Input area */
.input-area {{
  padding: 10px;
  margin-top: 12px;
  display: flex;
  gap: 8px;
  align-items: flex-start;
}}
textarea {{
  border-radius: 10px !important;
  border: 2px solid {PURPLE} !important;
  padding: 12px !important;
  font-size: 15px !important;
  width: 100%;
  min-height: 90px;
  resize: vertical;
  background: {BG_LIGHT if not st.session_state.dark else '#130512'};
  color: {'#111' if not st.session_state.dark else '#eee'};
}}

/* Small primary streamlit button - KEEP only one primary button on page */
div.stButton > button[kind="primary"] {{
  background-color: {PURPLE} !important;
  color: white !important;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 13px;
  border: none;
}}
div.stButton > button[kind="primary"]:hover {{
  background-color: {PURPLE_DARK} !important;
}}

/* Floating round send button */
.fab {{
  position: fixed;
  right: 26px;
  bottom: 26px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(180deg, {PURPLE} 0%, {PURPLE_DARK} 100%);
  box-shadow: 0 8px 20px rgba(0,0,0,0.2);
  display:flex;
  align-items:center;
  justify-content:center;
  cursor: pointer;
  z-index: 9999;
  border: 2px solid {YELLOW};
}}
.fab:hover {{
  transform: translateY(-3px);
}}
.fab .dot {{
  width: 10px;
  height: 10px;
  background: {YELLOW};
  border-radius: 50%;
}}

/* Small accent styles */
.accent {{
  color: {YELLOW};
  font-weight: 600;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ------------------------------
# JS: Enter to send (Enter=send, Shift+Enter=newline)
# Also floating button triggers the same submit by clicking the primary button
# ------------------------------
enter_js = """
<script>
document.addEventListener("keydown", function(e) {
    const ta = document.querySelector("textarea");
    if (!ta) return;

    // Only act if textarea is focused
    const active = document.activeElement;
    if (active !== ta) return;

    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        // click the first primary button (our send button)
        const btn = window.parent.document.querySelector('button[kind="primary"]');
        if (btn) btn.click();
    }
});
// Floating button handler: clicking it will also click the primary button
function triggerPrimary() {
    const btn = window.parent.document.querySelector('button[kind="primary"]');
    if (btn) btn.click();
}
</script>
"""
st.components.v1.html(enter_js, height=0)

# ------------------------------
# Top bar: header + theme toggle + instructions
# ------------------------------
col1, col2, col3 = st.columns([6, 1.2, 1.2])
with col1:
    st.markdown('<div class="header-title">Chat — Gemini 2.5 Flash</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#777; font-size:13px">Tema: <span class="accent">Morado</span> · Enter = enviar · Shift+Enter = salto de línea</div>', unsafe_allow_html=True)
with col2:
    # theme toggle
    def toggle_theme():
        st.session_state.dark = not st.session_state.dark
    st.button("Toggle tema", on_click=toggle_theme)
with col3:
    st.markdown(f"<div style='text-align:right; font-size:13px; color:#777'>Modelo: <span class='accent'>{MODEL_NAME}</span></div>", unsafe_allow_html=True)

st.write("")  # spacer

# ------------------------------
# Main layout: left chat, right quick actions (optional)
# ------------------------------
left_col, right_col = st.columns([3, 1])

with left_col:
    # Chat container (scrollable)
    st.markdown('<div class="chat-container" id="chatbox">', unsafe_allow_html=True)

    # Render messages
    for m in st.session_state.messages:
        time = m.get("time", "")
        if m["role"] == "user":
            st.markdown(f'<div class="msg-user">{st.markdown(m["text"], unsafe_allow_html=True) if False else st.write("")}</div>', unsafe_allow_html=True)
            # Because we cannot return the actual text via markdown in class, print again properly:
            st.markdown(f'<div style="display:none">_hidden_</div>', unsafe_allow_html=True)  # no-op
            # Direct HTML bubble with text:
            safe_text = m["text"].replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
            st.markdown(f'<div class="msg-user">{safe_text}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="msg-meta" style="text-align:right">{time}</div>', unsafe_allow_html=True)
        else:
            # assistant
            safe_text = m["text"].replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
            st.markdown(f'<div class="msg-bot">{safe_text}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="msg-meta">{time}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Input area: textarea + small send button (this is the single Streamlit primary button)
    with st.form(key="input_form", clear_on_submit=False):
        cols = st.columns([8, 1])
        with cols[0]:
            prompt = st.text_area(label="Escribe tu prompt aquí", value=st.session_state.prompt, key="input_text", height=110, placeholder="Escribe (Enter = enviar, Shift+Enter = nueva línea)", label_visibility="collapsed")
        with cols[1]:
            submit = st.form_submit_button("Enviar")  # this is the single primary button on page

        # On form submit via button (or Enter via JS clicking button),
        # proceed to send prompt
        if submit:
            txt = st.session_state.input_text.strip()
            if txt == "":
                st.warning("Escribe algo antes de enviar.")
            else:
                # Append user message
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.messages.append({"role": "user", "text": txt, "time": now})
                st.session_state.prompt = ""  # clear stored prompt
                st.session_state.input_text = ""  # clear textarea in UI (form not auto-cleared)
                # Show spinner while calling Gemini
                with st.spinner("Generando respuesta..."):
                    try:
                        model = genai.GenerativeModel(MODEL_NAME)
                        # Use generate_content; adapt to library signature
                        resp = model.generate_content(txt)
                        bot_text = getattr(resp, "text", str(resp))
                    except Exception as e:
                        bot_text = f"Error en la generación: {e}"

                now2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.messages.append({"role": "assistant", "text": bot_text, "time": now2})

                # rerun to render with new messages
                st.experimental_rerun()

with right_col:
    st.markdown("### Herramientas")
    st.markdown("- Presets rápidos")
    if st.button("Resumen corto"):
        # insert preset into input_text
        st.session_state.input_text = "Resume brevemente el siguiente texto:"
        st.experimental_rerun()
    if st.button("Explicar como para 5 años"):
        st.session_state.input_text = "Explícalo como si tuviera 5 años:"
        st.experimental_rerun()
    st.markdown("---")
    st.markdown("Opciones")
    st.checkbox("Mostrar timestamps", value=True, key="show_ts")

# ------------------------------
# Floating action button (HTML) - clicking calls triggerPrimary()
# ------------------------------
fab_html = f"""
<div class="fab" onclick="triggerPrimary()" title="Enviar">
  <div class="dot"></div>
</div>
"""
st.components.v1.html(fab_html, height=80)

# ------------------------------
# Auto-scroll chat to bottom (small JS — scroll the chat container)
# ------------------------------
scroll_js = """
<script>
const chat = parent.document.getElementById("chatbox");
if (chat) {
    chat.scrollTop = chat.scrollHeight;
}
</script>
"""
st.components.v1.html(scroll_js, height=0)
