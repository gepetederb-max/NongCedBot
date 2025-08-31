# app.py
import os
import base64
import google.generativeai as genai
import pandas as pd
import streamlit as st
from html import escape  # ✅ ป้องกัน HTML แตกในข้อความ
from prompt import PROMPT_WORKAW
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="NongCedBot | CED KMUTNB",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------- LOAD LOGO --------------------
# ใช้พาธจริงของคุณ
LOGO_PATH = "C:/Users/p/Documents/ChatBot/ChatBotCED/workaw_chatbot/NongCedBot/NongCedBot/assets/ced-logo.jpg"

def _img_as_base64(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

base64_logo = _img_as_base64(LOGO_PATH)

# -------------------- CSS THEME --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;500;700&display=swap');

.chat-wrap {
    font-family: 'Noto Sans Thai', sans-serif;
    margin-top: 1rem;
    max-width: 900px;
    margin-left: auto; margin-right: auto;
}

.chat-bubble {
    border-radius: 14px;
    padding: 12px 16px;
    margin: 8px 0;
    max-width: 100%;
    line-height: 1.5;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    animation: fadeIn 0.4s ease-in-out;
}

.user-bubble {
    background: linear-gradient(135deg, #4CAF50, #81C784); /* เขียว */
    color: #fff;
    margin-left: auto;
}

.assist-bubble {
    background: linear-gradient(135deg, #29B6F6, #FF7043); /* ฟ้า-ส้ม */
    color: #fff;
    margin-right: auto;
}

.msg-head {
    font-size: 0.85rem;
    font-weight: 700;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.role { padding-right: 4px; }

.badge {
    background: #fff;
    color: #29B6F6;
    font-size: 0.7rem;
    padding: 2px 6px;
    border-radius: 8px;
}

@keyframes fadeIn {
    from {opacity: 0; transform: translateY(6px);}
    to {opacity: 1; transform: translateY(0);}
}

/* Header logo */
.header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1rem;
}
.header img { height: 40px; }
.header h1 {
    font-size: 1.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #4CAF50, #29B6F6, #FF7043);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.markdown(
    f"""
    <div class="header">
        {'<img src="data:image/jpeg;base64,' + base64_logo + '" alt="logo">' if base64_logo else ''}
        <h1>NongCedBot</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------- Gemini Config --------------------
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", "AIzaSyCgsBcK44pVzAOMMh2PUAvwQtSdh-_AYr8"))
generation_config = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 1024,
    "response_mime_type": "text/plain",
}
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
}
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    safety_settings=SAFETY_SETTINGS,
    generation_config=generation_config,
    system_instruction=PROMPT_WORKAW
)

# -------------------- Sidebar --------------------
with st.sidebar:
    if base64_logo:
        st.image(LOGO_PATH, caption="Department of Computer Education | KMUTNB", use_container_width=True)
    st.markdown("### ⚙️ การตั้งค่า")
    if st.button("🧹 ล้างประวัติการสนทนา", use_container_width=True):
        st.session_state["messages"] = [{
            "role": "model",
            "content": "NongCedBot สวัสดีค่ะ 😊 ถามข้อมูลหลักสูตร/รายวิชา/หน่วยกิตของภาควิชาคอมพิวเตอร์ศึกษาได้เลยค่ะ"
        }]
        st.rerun()

# -------------------- Init Messages --------------------
if "messages" not in st.session_state or not st.session_state["messages"]:
    st.session_state["messages"] = [{
        "role": "model",
        "content": "NongCedBot สวัสดีค่ะ 😊 ฉันตอบคำถามเกี่ยวกับหลักสูตรภาควิชาคอมพิวเตอร์ศึกษา (KMUTNB) จากไฟล์ข้อมูลที่คุณอัปโหลด ลองพิมพ์เช่น “รายวิชาปี 1 เทอม 1” หรือ “วิชา OS กี่หน่วยกิต” ได้เลยค่ะ"
    }]

# -------------------- Load Data --------------------
file_path = "C:/Users/p/Documents/ChatBot/ChatBotCED/workaw_chatbot/NongCedBot/NongCedBot/NongCedBotFull.xlsx"
try:
    all_sheets = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")
    frames = []
    for name, dfx in all_sheets.items():
        dfx = dfx.copy()
        if not dfx.empty:
            dfx["sheet"] = name
            frames.append(dfx)
    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    file_content = df.to_csv(index=False)
except Exception as e:
    st.error(f"อ่านไฟล์ข้อมูลไม่สำเร็จ: {e}")
    st.stop()

# -------------------- Show Chat (safe text) --------------------
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
for msg in st.session_state["messages"]:
    bubble_cls = "user-bubble" if msg["role"] == "user" else "assist-bubble"
    role_label = "คุณ" if msg["role"] == "user" else "NongCedBot"
    badge = '<span class="badge">CED</span>' if msg["role"] != "user" else ""

    # ✅ ป้องกัน HTML แตก + คงบรรทัด
    safe_text = escape(str(msg["content"])).replace("\n", "<br>")

    st.markdown(
        f"""
        <div class="chat-bubble {bubble_cls}">
          <div class="msg-head">
            <span class="role">{role_label}</span> {badge}
          </div>
          <div style="white-space: pre-wrap;">{safe_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Chat Loop --------------------
prompt = st.chat_input("พิมพ์คำถามเกี่ยวกับหลักสูตร/รายวิชา เช่น “รายวิชาปี 2 เทอม 1” หรือ “วิชา Operating System กี่หน่วยกิต”")
if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    def generate_response():
        history = [{"role": m["role"], "parts": [{"text": m["content"]}]} for m in st.session_state["messages"]]
        history.insert(1, {"role": "user", "parts": [{"text": file_content}]})

        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(prompt)

        answer = response.text or "ขออภัยค่ะ ตอนนี้ฉันยังหาคำตอบให้ไม่ได้ ลองถามใหม่อีกครั้งนะคะ"
        st.session_state["messages"].append({"role": "model", "content": answer})
        st.chat_message("assistant").write(answer)

    generate_response()
