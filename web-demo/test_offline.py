"""Offline tests: logic only, Sarvam calls mocked. Run: python test_offline.py"""
import os, json
os.environ.setdefault("SARVAM_API_KEY", "x")
import sarvam_client as sv
from agent import check_eligibility, documents_for, run_agent
from kb_search import KB

# --- eligibility rules ---
assert check_eligibility({"age": 30, "has_work_experience": False})["track"] == "STT"
assert check_eligibility({"age": 50, "has_work_experience": True})["track"] == "RPL"
assert check_eligibility({"age": 50, "has_work_experience": False})["status"] == "not_eligible"
assert check_eligibility({"age": 16, "has_work_experience": True})["track"] == "STT"
assert check_eligibility({"age": 62, "has_work_experience": True})["status"] == "not_eligible"
assert check_eligibility({})["status"] == "need_info"
assert check_eligibility({"age": 30, "has_work_experience": False, "is_indian_citizen": False})["track"] is None
assert "work experience" in " ".join(documents_for("RPL")).lower()
print("eligibility rules OK")

# --- retrieval ---
kb = KB()
assert len(kb.chunks) >= 8
for q, expect in [("what age limit", "Age Eligibility"), ("which documents do I need", "Documents Required"),
                  ("how to apply online", "How to Apply"), ("do I have to pay fees", "free"),
                  ("tailor already working certificate", "RPL")]:
    top = kb.search(q, 3)
    assert any(expect.lower() in c["text"].lower() for c in top), (q, [c["text"][:40] for c in top])
print("retrieval OK")

# --- agent flow with mocked Sarvam ---
calls = []
def fake_chat(messages, model=None, temperature=0.2):
    calls.append(model or sv.CHAT_MODEL)
    if model == sv.REASON_MODEL:
        return '```json\n{"age": 35, "has_work_experience": true, "trade": "tailor"}\n```'
    assert "ELIGIBILITY RESULT" in messages[0]["content"] and "RPL" in messages[0]["content"]
    return "आप आरपीएल के लिए पात्र हो सकते हैं।"
sv.chat = fake_chat
sv.translate = lambda text, target, source="en-IN": f"[{target}] {text}"
out = run_agent("मैं 35 साल का दर्जी हूँ", "hi-IN", [], {})
assert out["elig"]["track"] == "RPL" and out["checklist"][0].startswith("[hi-IN]")
assert sv.REASON_MODEL in calls and sv.CHAT_MODEL in calls
assert out["profile"]["trade"] == "tailor"
print("agent flow OK, models used:", set(calls))

# need_info path
sv.chat = lambda m, model=None, temperature=0.2: '{"age": null}' if model == sv.REASON_MODEL else "आपकी उम्र कितनी है?"
o2 = run_agent("PMKVY क्या है", "hi-IN", [], {})
assert o2["elig"]["status"] == "need_info" and o2["checklist"] == []
print("need_info path OK\nALL TESTS PASSED")
