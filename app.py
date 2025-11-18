import streamlit as st
import google.generativeai as genai
from datetime import datetime
import streamlit.components.v1 as components

# ----------------------------
# Config
# ----------------------------
st.set_page_config(page_title="Gemini WebApp", layout="wide")
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
MODEL_NAME = "gemini-2.5-flash"

# ----------------------------
# Session state
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # list of {"role":"user"|"ai", "text": str, "time": str}

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# ----------------------------
# Styles
# ----------------------------
st.markdown(
    """
    <style>
    body { background-color: #ffffff; }
    .title { color: #5b2e91; font-size: 28px; font-weight:700; margin-bottom:12px; }
    .top-note { color: #444; margin-bottom:18px; }
    .block { border-radius:10px; padding:20px; margin-bottom:16px; font-size:16px; line-height:1.6; color:#222; }
    .user-block { background: rgba(250,245,255,0.75); border-left:6px solid #ffda55; }
    .ai-block { background: rgba(243,234,255,0.9); border-left:6px solid #5b2e91; }
    /* floating input area at bottom */
    .input-floating {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 14px 18px;
        background: #faf5ff;
        border-top: 3px solid #5b2e91;
        z-index: 9999;
        box-shadow: 0 -6px 18px rgba(0,0,0,0.04);
    }
    textarea {
        border-radius:10px !important;
        border:2px solid #5b2e91 !important;
        padding:10px !important;
        font-size:15px !important;
        color: #222 !important;
        background: #fff !important;
        width: 100% !important;
        min-height: 80px !important;
        resize: vertical;
    }
    .send-btn button {
        background-color: #5b2e91 !important;
        color: white !important;
        border-radius:8px !important;
        border:2px solid #ffda55 !important;
        padding: 8px 14px !important;
        font-size:14px !important;
    }
    .send-btn button:hover { background-color: #43206d !important; }
    /* add small bottom padding so last messages aren't covered */
    .messages-padding { padding-bottom: 140px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Header
# ----------------------------
st.markdown("<div class='title'>Gemini WebApp</div>", unsafe_allow_html=True)
st.markdown("<div class='top-note'>Caja de texto abajo — Enter = enviar · Shift+Enter = nueva línea</div>", unsafe_allow_html=True)

# ----------------------------
# Messages history (above)
# ----------------------------
container = st.container()
with container:
    # extra padding so bottom input doesn't overlap last item
    st.markdown("<div class='messages-padding'></div>", unsafe_allow_html=True)
    for m in st.session_state.history:
        ts = m.get("time", "")
        if m["role"] == "user":
            st.markdown(f"<div class='block user-block'>{m['text']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='block ai-block'>{m['text']}</div>", unsafe_allow_html=True)

# ----------------------------
# Floating input area (always below)
# ----------------------------
st.markdown("<div class='input-floating'>", unsafe_allow_html=True)
cols = st.columns([10, 1])
with cols[0]:
    # textarea bound to st.session_state["user_input"]
    user_text = st.text_area("", key="user_input", value=st.session_state.user_input, label_visibility="collapsed", placeholder="Escribe tu prompt aquí...")
with cols[1]:
    send_clicked = st.button("Enviar", key="send_primary")  # this will be the primary button JS clicks
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Send logic (python side)
# ----------------------------
def call_gemini(prompt_text: str) -> str:
    """A thin wrapper: call Gemini model and return response text (adapt to your SDK)."""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        resp = model.generate_content(prompt_text)
        # try common attribute
        if hasattr(resp, "text"):
            return resp.text
        return str(resp)
    except Exception as e:
        return f"Error en la generación: {e}"

if send_clicked and st.session_state.user_input.strip():
    txt = st.session_state.user_input.strip()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.history.append({"role": "user", "text": txt, "time": now})

    # call model (spinner)
    with st.spinner("Generando respuesta..."):
        out = call_gemini(txt)
    now2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.history.append({"role": "ai", "text": out, "time": now2})

    # clear input properly
    st.session_state["user_input"] = ""
    # rerun so UI updates and textarea empties
    st.experimental_rerun()

# ----------------------------
# Robust JS: Attach keydown handler to textarea
# Shift+Enter => newline, Enter => click send button
# We use a polling strategy to ensure we attach the handler once the DOM element exists.
# ----------------------------
js_code = """
<script>
(function() {
  // avoid adding multiple listeners
  if (window._streamlit_enter_handler_attached) return;
  window._streamlit_enter_handler_attached = true;

  function attach() {
    // textarea inside Streamlit page
    const ta = document.querySelector('textarea');
    // primary send button (Streamlit renders button[kind="primary"])
    const sendBtn = document.querySelector('button[kind="primary"]');

    if (!ta) return false;  // not ready yet
    // If sendBtn not found here, try parent document (some embed cases)
    if (!sendBtn && window.parent) {
      try { sendBtn = window.parent.document.querySelector('button[kind="primary"]'); } catch(e) {}
    }
    if (!sendBtn) {
      // It's possible Streamlit renders button with no kind attr in some versions; fallback find by text "Enviar"
      const allBtns = Array.from(document.querySelectorAll('button'));
      for (const b of allBtns) {
        if (b.innerText && b.innerText.trim().toLowerCase() === 'enviar') {
          sendBtn = b;
          break;
        }
      }
    }

    if (!ta) return false;
    // Add a single handler (idempotent)
    if (!ta._hasStreamlitHandler) {
      ta._hasStreamlitHandler = true;
      ta.addEventListener('keydown', function(e) {
        // Shift+Enter -> insert newline
        if (e.key === 'Enter' && e.shiftKey) {
          // let the browser insert newline naturally
          return;
        }
        // Enter (no shift) -> send
        if (e.key === 'Enter' && !e.shiftKey) {
          // prevent default newline
          e.preventDefault();
          // click send button if found
          if (sendBtn) {
            sendBtn.click();
          } else {
            // fallback: try to submit by finding button with text "Enviar"
            const allBtns = Array.from(document.querySelectorAll('button'));
            for (const b of allBtns) {
              if (b.innerText && b.innerText.trim().toLowerCase() === 'enviar') {
                b.click();
                break;
              }
            }
          }
        }
      }, false);
      return true;
    }
    return true;
  }

  // Try attach repeatedly for up to ~3 seconds
  let tries = 0;
  const interval = setInterval(function() {
    tries += 1;
    const ok = attach();
    if (ok || tries > 30) {
      clearInterval(interval);
    }
  }, 100);
})();
</script>
"""
components.html(js_code, height=0)
