"""PMKVY agent: profile extraction -> eligibility tool -> retrieval -> grounded answer."""
import json, re
import sarvam_client as sv
from kb_search import KB

KB_INDEX = KB()

LANG_NAMES = {"hi-IN": "Hindi", "en-IN": "English", "mr-IN": "Marathi", "ta-IN": "Tamil",
              "te-IN": "Telugu", "bn-IN": "Bengali", "gu-IN": "Gujarati",
              "kn-IN": "Kannada", "ml-IN": "Malayalam", "pa-IN": "Punjabi", "od-IN": "Odia"}

PROFILE_PROMPT = """Extract facts about the user from the conversation. Reply with ONLY JSON:
{"age": int|null, "has_work_experience": true|false|null, "trade": string|null,
 "is_indian_citizen": true|null, "has_aadhaar": true|null, "has_bank_account": true|null,
 "education": string|null, "state": string|null}
Use null when not stated. Do not guess."""


def _json(txt):
    m = re.search(r"\{.*\}", txt, re.S)
    return json.loads(m.group(0)) if m else {}


def extract_profile(history):
    convo = "\n".join(f"{m['role']}: {m['content']}" for m in history if m["role"] == "user")
    try:
        return _json(sv.chat([{"role": "system", "content": PROFILE_PROMPT},
                              {"role": "user", "content": convo}],
                             model=sv.REASON_MODEL, temperature=0))
    except Exception:
        return {}


def merge(old, new):
    out = dict(old)
    out.update({k: v for k, v in (new or {}).items() if v is not None})
    return out


# ---- deterministic "tool": eligibility rules (no LLM guessing on rules) ----
def check_eligibility(p):
    missing, notes, track = [], [], None
    age = p.get("age")
    exp = p.get("has_work_experience")
    if age is None:
        missing.append("age")
    if exp is None:
        missing.append("work experience in a trade")
    if age is not None:
        if exp:
            if 18 <= age <= 59:
                track = "RPL"
            elif age < 18 and 15 <= age:
                track = "STT"
                notes.append("RPL needs age 18+, but STT is possible at 15-45.")
            else:
                notes.append("Age is outside the RPL range (18-59).")
        elif exp is False:
            if 15 <= age <= 45:
                track = "STT"
            else:
                notes.append("Age is outside the STT range (15-45); RPL (18-59) may fit if you work in a trade.")
    if p.get("is_indian_citizen") is False:
        track = None
        notes.append("PMKVY is for Indian nationals.")
    status = "need_info" if (missing and not track) else ("likely_eligible" if track else "not_eligible")
    return {"status": status, "track": track, "missing": missing, "notes": notes}


DOCS = ["Aadhaar card (for e-KYC)", "Bank account details in your name",
        "Mobile number", "Education details", "Passport-size photo"]
DOCS_RPL_EXTRA = ["Proof or details of your work experience in your trade"]


def documents_for(track):
    return DOCS + (DOCS_RPL_EXTRA if track == "RPL" else [])


SYSTEM = """You are 'Kaushal Saathi', a friendly voice assistant that helps Indians with the PMKVY skilling scheme.
Rules:
- Answer ONLY from the CONTEXT and ELIGIBILITY RESULT below. If the answer is not there, say you are not sure and suggest asking the nearest training centre or skillindia.gov.in.
- Reply in {lang}. Use very simple words, 3-5 short sentences, suitable for being read aloud. No markdown, no lists.
- If ELIGIBILITY status is need_info, ask ONE short question about the first missing item and nothing else.
- Never ask for Aadhaar or bank numbers. Remind the user that PMKVY training is free.
ELIGIBILITY RESULT: {elig}
CONTEXT:
{ctx}"""


def run_agent(user_text, lang, history, profile):
    lang = lang if lang in LANG_NAMES else "en-IN"  # Bulbul/Mayura/105B support 11 languages
    history = history + [{"role": "user", "content": user_text}]
    profile = merge(profile, extract_profile(history))
    elig = check_eligibility(profile)
    hits = KB_INDEX.search(user_text + " " + (profile.get("trade") or "") + " " + (elig["track"] or ""), k=3)
    ctx = "\n\n".join(h["text"] for h in hits) or "(no context found)"
    system = SYSTEM.format(lang=LANG_NAMES.get(lang, "Hindi"), elig=json.dumps(elig), ctx=ctx)
    reply = sv.chat([{"role": "system", "content": system}] + history[-6:])
    checklist = []
    if elig["track"]:
        docs = documents_for(elig["track"])
        checklist = [sv.translate(d, lang) for d in docs]
    return {"lang": lang, "reply": reply, "profile": profile, "elig": elig, "sources": [h["source"] for h in hits],
            "checklist": checklist, "retrieved": [h["text"][:120] for h in hits],
            "history": history + [{"role": "assistant", "content": reply}]}
