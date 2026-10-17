"""Website + API.  Run:  uvicorn server:app --reload --port 8000   → http://localhost:8000"""
import base64, os, uuid
from typing import Optional
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
import sarvam_client as sv
from agent import run_agent, LANG_NAMES, KB_INDEX

HERE = os.path.dirname(__file__)
app = FastAPI(title="Kaushal Saathi – PMKVY assistant")
SESSIONS: dict = {}


@app.get("/", response_class=HTMLResponse)
def index():
    html = open(os.path.join(HERE, "static", "index.html"), encoding="utf-8").read()
    snippet_path = os.path.join(HERE, "widget_snippet.html")  # paste Sarvam Voice Agents embed code here
    snippet = open(snippet_path, encoding="utf-8").read() if os.path.exists(snippet_path) else ""
    return html.replace("<!--SARVAM_WIDGET-->", snippet)


@app.get("/api/health")
def health():
    return {"ok": True, "chunks": len(KB_INDEX.chunks), "languages": LANG_NAMES}


@app.post("/api/chat")
def chat(sid: str = Form(...), lang: str = Form("hi-IN"), text: str = Form(""),
         speak: bool = Form(True), audio: Optional[UploadFile] = File(None)):
    try:
        heard = text
        if audio is not None:
            heard, lang = sv.stt(audio.file.read(), audio.filename or "audio.wav")   # Saaras v4
        if not heard.strip():
            return JSONResponse({"error": "I could not hear anything. Please try again."}, 400)
        s = SESSIONS.setdefault(sid, {"history": [], "profile": {}})
        out = run_agent(heard, lang, s["history"], s["profile"])                      # 105B + tools + Mayura
        s["history"], s["profile"] = out["history"], out["profile"]
        audio_b64 = None
        if speak:
            try:
                audio_b64 = base64.b64encode(sv.tts(out["reply"], out["lang"])).decode()  # Bulbul v3
            except Exception:
                pass
        return {"heard": heard, "lang": out["lang"], "reply": out["reply"], "checklist": out["checklist"],
                "elig": out["elig"], "profile": out["profile"], "sources": out["sources"], "audio": audio_b64}
    except Exception as e:
        return JSONResponse({"error": str(e)}, 500)


GREETING_EN = ("Hello! I am Kaushal Saathi. I explain government schemes like PMKVY in very simple words, "
               "and I can guide you step by step. How can I help you today?")
_GREET: dict = {}


@app.get("/api/greet")
def greet(lang: str = "en-IN", speak: bool = False):
    lang = lang if lang in LANG_NAMES else "en-IN"
    if lang not in _GREET:
        try:
            _GREET[lang] = GREETING_EN if lang == "en-IN" else sv.translate(GREETING_EN, lang)   # Mayura
        except Exception:
            _GREET[lang] = GREETING_EN
    audio = None
    if speak:
        try:
            audio = base64.b64encode(sv.tts(_GREET[lang], lang)).decode()   # Bulbul v3
        except Exception:
            pass
    return {"lang": lang, "text": _GREET[lang], "audio": audio}


@app.post("/api/reset")
def reset(sid: str = Form(...)):
    SESSIONS.pop(sid, None)
    return {"ok": True}


# ---- llms.txt so AI crawlers / judges' tools can read the knowledge base ----
@app.get("/llms.txt", response_class=PlainTextResponse)
def llms_txt():
    heads = []
    for c in KB_INDEX.chunks:
        h = c["text"].split("\n", 1)[0].lstrip("# ").strip()
        heads.append(f"- {h} ({c['source']})")
    return ("# Kaushal Saathi\n\n"
            "> Voice-first multilingual assistant that tells Indians whether they qualify for PMKVY "
            "(Pradhan Mantri Kaushal Vikas Yojana) free skill training, which documents to keep ready, "
            "and how to apply. Built on Sarvam AI (Saaras, Sarvam-105B, Mayura, Bulbul, Sarvam Vision).\n\n"
            "## Knowledge base\n- [Full text](/llms-full.txt): all PMKVY facts the assistant answers from\n\n"
            "## Topics\n" + "\n".join(heads) + "\n\n## API\n- POST /api/chat: text or audio in, grounded answer and audio out\n"
            "- GET /api/health: status\n")


@app.get("/llms-full.txt", response_class=PlainTextResponse)
def llms_full():
    return "\n\n".join(c["text"] for c in KB_INDEX.chunks)
