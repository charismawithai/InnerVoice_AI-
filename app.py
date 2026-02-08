from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os
from dotenv import load_dotenv
import streamlit as st
from groq import Groq

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="InnerVoice AI", page_icon="🧠", layout="centered")

# ---------------- LOAD API ----------------
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------------- CHAT MEMORY ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- PDF GENERATOR ----------------
def create_pdf(text):
    doc = SimpleDocTemplate("growth_plan.pdf")
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("InnerVoice AI – Personal Growth Plan", styles['Title']))
    story.append(Paragraph(text, styles['BodyText']))
    doc.build(story)

# ---------------- EMOTION DETECTION ----------------
def detect_emotion(user_text):
    emotion_prompt = f"""
Detect the MAIN emotion from the message.
Return ONLY one word.

Options:
Anxiety, Confusion, Motivation, Confidence, Fear, Sadness, Excitement

Message: {user_text}
"""

    emotion_chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        max_tokens=10,
        messages=[{"role":"user","content":emotion_prompt}]
    )

    return emotion_chat.choices[0].message.content.strip()

# ---------------- LONG ROADMAP GENERATOR (FIXED 🔥) ----------------
def generate_roadmap(user_text):

    roadmap_prompt = f"""
Create a VERY DETAILED step-by-step career roadmap.

IMPORTANT RULES:
- Minimum length: 1200 words
- MUST finish the roadmap completely
- Do NOT stop mid sentence
- End with a motivational closing paragraph

Structure EXACTLY like this:

PHASE 1 — Foundation (0-3 months)
PHASE 2 — Core Skills (4-6 months)
PHASE 3 — Advanced Skills (7-9 months)
PHASE 4 — Job Preparation (10-12 months)

Each phase MUST include:
• Skills to learn
• Tools
• Projects
• Practice plan
• Interview prep tips

User request:
{user_text}
"""

    roadmap_chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        max_tokens=1800,   # 🔥 BIG FIX (was 500)
        messages=[{"role":"user","content":roadmap_prompt}]
    )

    return roadmap_chat.choices[0].message.content


# ---------------- SYSTEM PROMPT ----------------
system_prompt = """
You are InnerVoice AI — an emotionally intelligent life coach.

Tone rules:
Anxiety/Fear → calming
Sadness → supportive
Confusion → step-by-step
Motivation/Confidence → energetic

Always give emotional support + practical steps.
"""

# ==================================================
# 🎨 HERO HEADER
# ==================================================
st.markdown("""
<h1 style='text-align:center;'>🧠 InnerVoice AI</h1>
<p style='text-align:center;font-size:22px;color:gray;'>
Your AI Life Coach • Career Therapist • Confidence Builder
</p>
""", unsafe_allow_html=True)

# ==================================================
# ⭐ FEATURE CARDS
# ==================================================
st.markdown("### What I can help you with")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("💬 Emotional Support\nTalk when you feel lost or stressed")

with col2:
    st.info("🛤 Career Roadmaps\nGet step-by-step career plans")

with col3:
    st.info("📄 Download Growth Plan\nSave your progress as PDF")

st.divider()

# ---------------- CHAT INPUT ----------------
user_input = st.chat_input("Tell me what you're going through...")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})

    roadmap_keywords = [
        "roadmap","career path","career plan","how do i become",
        "how to become","how can i become","how do i start",
        "how to start","guide me","learning path"
    ]

    # 🔥 SHOW LOADER (UX BOOST)
    with st.spinner("Thinking deeply about your situation..."):

        # ---------------- ROADMAP MODE ----------------
        if any(word in user_input.lower() for word in roadmap_keywords):
            roadmap = generate_roadmap(user_input)
            st.session_state.messages.append({"role":"assistant","content":roadmap})

        # ---------------- EMOTIONAL CHAT MODE ----------------
        else:
            emotion = detect_emotion(user_input)

            chat = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                temperature=0.8,
                max_tokens=900,   # 🔥 increased
                messages=[
                    {"role":"system","content":system_prompt},
                    {"role":"user","content":f"Emotion: {emotion}\nMessage: {user_input}"}
                ]
            )

            reply = chat.choices[0].message.content
            st.session_state.messages.append({"role":"assistant","content":reply})

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------- PDF DOWNLOAD ----------------
if len(st.session_state.messages) > 1:
    if st.button("📄 Download My Growth Plan"):
        full_chat = ""
        for msg in st.session_state.messages:
            full_chat += f"{msg['role'].upper()}: {msg['content']}\n\n"

        create_pdf(full_chat)

        with open("growth_plan.pdf", "rb") as file:
            st.download_button(
                label="⬇️ Click to Download PDF",
                data=file,
                file_name="InnerVoice_Growth_Plan.pdf",
                mime="application/pdf"
            )
