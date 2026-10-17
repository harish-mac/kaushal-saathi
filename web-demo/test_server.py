"""Website/API tests with Sarvam mocked. Run: python test_server.py"""
import os, base64
os.environ.setdefault("SARVAM_API_KEY", "x")
import sarvam_client as sv
from fastapi.testclient import TestClient
import server

def fake_chat(messages, model=None, temperature=0.2):
    if model == sv.REASON_MODEL:
        return '{"age": 35, "has_work_experience": true, "trade": "tailor"}'
    return "आप आरपीएल के लिए पात्र हो सकते हैं।"
sv.chat = fake_chat
sv.translate = lambda t, target, source="en-IN": f"[{target}] {t}"
sv.tts = lambda text, lang="hi-IN": b"RIFFfakewav"
sv.stt = lambda b, filename="a.wav", mode="transcribe": ("मैं 35 साल का दर्जी हूँ", "ur-IN")  # unsupported TTS lang → falls back

c = TestClient(server.app)
assert "Kaushal Saathi" in c.get("/").text
assert c.get("/api/health").json()["chunks"] >= 8
r = c.post("/api/chat", data={"sid": "s1", "lang": "hi-IN", "text": "मैं 35 साल का दर्जी हूँ"}).json()
assert r["elig"]["track"] == "RPL" and r["checklist"] and base64.b64decode(r["audio"]) == b"RIFFfakewav", r
r2 = c.post("/api/chat", data={"sid": "s2"}, files={"audio": ("a.wav", b"123", "audio/wav")}).json()
assert r2["heard"].startswith("मैं") and r2["lang"] == "en-IN", r2          # ur-IN normalised to English default
assert c.post("/api/chat", data={"sid": "s3", "text": "  "}).status_code == 400
assert len(server.SESSIONS["s1"]["history"]) == 2
assert c.post("/api/reset", data={"sid": "s1"}).json()["ok"] and "s1" not in server.SESSIONS
t = c.get("/llms.txt").text
assert t.startswith("# Kaushal Saathi") and "PMKVY" in t and "Age Eligibility" in t
assert "Documents Required" in c.get("/llms-full.txt").text
g = c.get("/api/greet?lang=ta-IN&speak=true").json()
assert g["lang"] == "ta-IN" and g["text"].startswith("[ta-IN]") and g["audio"], g
g2 = c.get("/api/greet?lang=xx-XX").json()
assert g2["lang"] == "en-IN" and g2["text"].startswith("Hello") and g2["audio"] is None, g2
assert 'value="en-IN"' in c.get("/").text or '$("lang").value="en-IN"' in c.get("/").text
print("SERVER TESTS PASSED")
