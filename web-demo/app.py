import streamlit as st
import sarvam_client as sv
from agent import run_agent, LANG_NAMES

st.set_page_config(page_title="Kaushal Saathi", page_icon="🛠️")
st.title("🛠️ Kaushal Saathi — PMKVY Voice Assistant")
st.caption("Speak in your language. Find out how to get free, government-certified skill training.")

for k, v in {"history": [], "profile": {}, "turns": []}.items():
    st.session_state.setdefault(k, v)

with st.sidebar:
    lang = st.selectbox("Reply language (for typed input)", list(LANG_NAMES), index=list(LANG_NAMES).index("en-IN"), format_func=LANG_NAMES.get)
    autoplay = st.checkbox("Speak replies", True)
    if st.button("Reset conversation"):
        st.session_state.update(history=[], profile={}, turns=[]); st.rerun()
    st.subheader("🧠 Agent memory")
    st.json({k: v for k, v in st.session_state.profile.items() if v is not None})

audio = st.audio_input("🎤 Speak")
typed = st.chat_input("...or type your question")

text = None
if audio and audio.file_id != st.session_state.get("last_audio"):
    st.session_state.last_audio = audio.file_id
    with st.spinner("Listening (Saaras v4)..."):
        text, lang = sv.stt(audio.getvalue())
        lang = lang if lang in LANG_NAMES else "en-IN"
elif typed:
    text = typed

if text:
    with st.spinner("Thinking (Sarvam-105B)..."):
        try:
            out = run_agent(text, lang, st.session_state.history, st.session_state.profile)
        except Exception as e:
            st.error(f"Something went wrong: {e}"); st.stop()
    st.session_state.history = out["history"]
    st.session_state.profile = out["profile"]
    audio_bytes = None
    if autoplay:
        try: audio_bytes = sv.tts(out["reply"], out["lang"])
        except Exception as e: st.warning(f"Voice unavailable: {e}")
    st.session_state.turns.append({"user": text, **out, "audio": audio_bytes})

for t in st.session_state.turns:
    with st.chat_message("user"): st.write(t["user"])
    with st.chat_message("assistant"):
        st.write(t["reply"])
        if t.get("audio"): st.audio(t["audio"], format="audio/wav")
        if t["checklist"]:
            st.success("📄 Documents to keep ready: " + " • ".join(t["checklist"]))
            st.info("Apply: Skill India Digital Hub (SIDH) → PMKVY → pick a nearby batch. Training is FREE. Never pay anyone.")
        with st.expander("🔍 How the agent decided"):
            st.write("**Eligibility tool:**", t["elig"])
            st.write("**Sources used:**", t["sources"])
