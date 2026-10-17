"""Thin wrappers around Sarvam APIs. One function per model."""
import os, re, base64, requests
from dotenv import load_dotenv
load_dotenv()

BASE = "https://api.sarvam.ai"
CHAT_MODEL = os.getenv("CHAT_MODEL", "sarvam-105b-conversations")
REASON_MODEL = os.getenv("REASON_MODEL", "sarvam-105b")
SPEAKER = os.getenv("TTS_SPEAKER", "shubh")


def _key():
    return {"api-subscription-key": os.environ["SARVAM_API_KEY"]}


def _json_h():
    return {**_key(), "Content-Type": "application/json"}


# 1) Saaras v4 : speech -> text (+ detected language)
def stt(audio_bytes: bytes, filename="audio.wav", mode="transcribe"):
    r = requests.post(
        f"{BASE}/speech-to-text", headers=_key(),
        files={"file": (filename, audio_bytes, "audio/wav")},
        data={"model": "saaras:v4", "mode": mode}, timeout=60)
    r.raise_for_status()
    j = r.json()
    return j.get("transcript", ""), j.get("language_code") or "hi-IN"


# 2) Sarvam-105B family : reasoning + conversation
def chat(messages, model=None, temperature=0.2):
    payload = {"model": model or CHAT_MODEL, "messages": messages, "temperature": temperature}
    for path in ("/v1/chat/completions", "/chat/completions"):
        r = requests.post(BASE + path, headers=_json_h(), json=payload, timeout=90)
        if r.status_code != 404:
            break
    r.raise_for_status()
    txt = r.json()["choices"][0]["message"]["content"] or ""
    return re.sub(r"<think>.*?</think>", "", txt, flags=re.S).strip()


# 3) Mayura : translate deterministic content (checklists) so facts never drift
def translate(text: str, target: str, source="en-IN"):
    if not text or target == source or target.startswith("en"):
        return text
    r = requests.post(
        f"{BASE}/translate", headers=_json_h(),
        json={"input": text[:1000], "source_language_code": source,
              "target_language_code": target, "model": "mayura:v1"}, timeout=60)
    r.raise_for_status()
    return r.json().get("translated_text", text)


# 4) Bulbul v3 : text -> speech
def tts(text: str, lang="hi-IN"):
    r = requests.post(
        f"{BASE}/text-to-speech", headers=_json_h(),
        json={"text": text[:900], "target_language_code": lang,
              "model": "bulbul:v3", "speaker": SPEAKER}, timeout=60)
    r.raise_for_status()
    return base64.b64decode(r.json()["audios"][0])


# 5) Sarvam Vision : PDF/image -> markdown (used by ingest.py)
def digitise(path: str, out_zip: str, language="en-IN"):
    from sarvamai import SarvamAI
    client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])
    job = client.document_intelligence.create_job(language=language, output_format="md")
    job.upload_file(path)
    job.start()
    job.wait_until_complete()
    job.download_output(out_zip)
    return out_zip
