"""RUN THIS FIRST with your real key. Checks every Sarvam model used."""
import sarvam_client as sv, traceback

def t(name, fn):
    try:
        print("OK  ", name, "->", str(fn())[:80])
    except Exception as e:
        print("FAIL", name, "->", e)

t("Sarvam-105B chat", lambda: sv.chat([{"role": "user", "content": "Say hi in Hindi in 5 words"}]))
t("Sarvam-105B reasoning", lambda: sv.chat([{"role": "user", "content": "2+2?"}], model=sv.REASON_MODEL))
t("Mayura translate", lambda: sv.translate("Aadhaar card", "hi-IN"))
t("Bulbul TTS", lambda: len(sv.tts("नमस्ते, पीएमकेवीवाई में आपका स्वागत है", "hi-IN")))
open("sample.wav", "wb").write(sv.tts("मैं पैंतीस साल का हूँ और सिलाई का काम करता हूँ", "hi-IN"))
t("Saaras v4 STT (on the TTS clip)", lambda: sv.stt(open("sample.wav", "rb").read()))
