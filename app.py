import streamlit as st
import google.generativeai as genai
from datetime import datetime
import streamlit.components.v1 as components

# ----------------------------------
# CONFIG
# ----------------------------------
st.set_page_config(page_title="Gemini WebApp", layout="wide")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
MODEL_NAME = "gemini-2.5-flash"

# ----------------------------------
# SESSION STATE
# ----------------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # Chats

if "user_input" not in st.session_state:
    st.session_state.user_input = ""


# ----------------------------------
# STYLES
# ----------------------------------
st.markdown("""
<style>
body { background-color: #ffffff; }

/* Title */
.title {
    color: #5b2e91;
    font-size: 30px;
    font-weight: 700;
    margin-bottom: 20px;
}

/* Message blocks */
.block {
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 14px;
    font-size: 16px;
    line-height: 1.6;
}

.user-block {
    background: rgba(250,245,255,0.8);
    border-left: 6px solid #ffda55;
}

.ai-block {
    background: rgba(235,225,250,0.9);
    border-left: 6px solid #5b2e91;
}

/* Space so messages aren't hidden behind bottom bar */
.messages-padding {
    padding-bottom: 150px;
}

/* Bottom input bar */
.input-floating {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 16px 20px;
    background: #faf5ff;
    border-top: 3px solid #5b2e91;
    z-index: 9999;
    box-shadow: 0 -4px 16px rgba(0,0,0,0.05);
}

textarea {
    border-radius: 10px !important;
    border: 2px solid #5b2e91 !important;
    padding: 10px !important;
    font-size: 15px !important;
    color: #222 !important;
    background: #ffffff !important;
    width: 100% !important;
    min-height: 80px !important;
    resize: vertical;
}

/* Button */
.send-btn button {
    background-color: #5b2e91 !important;
    color: white !important;
    border-radius: 8px !important;
    border: 2px solid #ffda55 !important;
    padding: 8px 14px !important;
    font-size: 14px !important;
}
.send-btn button:hover {
    background-color: #43206d !important;
}
</style>
""", unsafe_allow_html=True)


# ----------------------------------
# GEMINI CALL
# ----------------------------------
def call_gemini(prompt):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        if hasattr(response, "text"):
            return response.text
        return str(response)
    except Exception as e:
        return f"Error en la generación: {e}"


# ----------------------------------
# CALLBACK: send message
# ----------------------------------
def send_message():
    txt = st.session_state.user_input.strip()
    if not txt:
        return

    st.session_state.history.append({"role": "user", "text": txt})

    out = call_gemini(txt)
    st.session_state.history.append({"role": "ai", "text": out})

    # Clean BEFORE widget rendering
    st.session_state.user_input = ""


# ----------------------------------
# HEADER
# ----------------------------------
st.markdown("<div class='title'>Gemini WebApp</div>", unsafe_allow_html=True)


# ----------------------------------
# CHAT HISTORY
# ----------------------------------
container = st.container()
with container:
    st.markdown("<div class='messages-padding'></div>", unsafe_allow_html=True)

    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(
                f"<div class='block user-block'>{msg['text']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='block ai-block'>{msg['text']}</div>",
                unsafe_allow_html=True
            )


# ----------------------------------
# FLOATING INPUT BAR
# ----------------------------------
st.markdown("<div class='input-floating'>", unsafe_allow_html=True)

col1, col2 = st.columns([10, 1])

with col1:
    st.text_area(
        "",
        key="user_input",
        label_visibility="collapsed",
        placeholder="Escribe tu prompt...",
    )

with col2:
    st.button("Enviar", key="send_primary", on_click=send_message, help="Enviar mensaje")

st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------
# JS: Enter = enviar, Shift+Enter = nueva línea
# ----------------------------------
components.html("""
<script>
(function() {
  if (window._enterFixApplied) return;
  window._enterFixApplied = true;

  function attach() {
    const ta = document.querySelector("textarea");
    if (!ta) return false;

    let sendBtn = document.querySelector('button[kind="primary"]');
    if (!sendBtn) {
      const btns = [...document.querySelectorAll("button")];
      sendBtn = btns.find(b => b.innerText.trim().toLowerCase() === "enviar");
    }

    if (!sendBtn) return false;

    if (!ta._listenerAttached) {
      ta._listenerAttached = true;

      ta.addEventListener("keydown", function(e) {
        if (e.key === "Enter" && e.shiftKey) {
          return; // allow newline
        }
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          sendBtn.click();
        }
      });
    }

    return true;
  }

  let tries = 0;
  const interval = setInterval(() => {
    tries += 1;
    if (attach() || tries > 40) {
      clearInterval(interval);
    }
  }, 100);
})();
</script>
""", height=0)
