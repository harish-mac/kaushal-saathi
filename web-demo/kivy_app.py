"""Kivy client (desktop / Android via buildozer). Talks to server.py.
Run server first:  uvicorn server:app --port 8000
Then:              python kivy_app.py            (set SERVER_URL for a remote server)"""
import base64, os, tempfile, threading, uuid
import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

SERVER = os.getenv("SERVER_URL", "http://localhost:8000")
LANGS = {"Hindi": "hi-IN", "English": "en-IN", "Marathi": "mr-IN", "Tamil": "ta-IN", "Telugu": "te-IN",
         "Bengali": "bn-IN", "Gujarati": "gu-IN", "Kannada": "kn-IN", "Malayalam": "ml-IN",
         "Punjabi": "pa-IN", "Odia": "od-IN"}
# Kivy's default font lacks Indic glyphs: set FONT to a Noto Sans file you ship (e.g. NotoSansDevanagari-Regular.ttf)
FONT = os.getenv("KIVY_FONT", "Roboto")


class Root(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=10, spacing=8, **kw)
        self.sid = str(uuid.uuid4())
        self.add_widget(Label(text="Kaushal Saathi · PMKVY", size_hint_y=None, height=40, font_size=22, bold=True))
        self.lang = Spinner(text="Hindi", values=list(LANGS), size_hint_y=None, height=44, font_name=FONT)
        self.add_widget(self.lang)
        self.out = Label(text="Type your situation, e.g. 'I am 35 and work as a tailor'", font_name=FONT,
                         size_hint_y=None, halign="left", valign="top", markup=False)
        self.out.bind(width=lambda *_: setattr(self.out, "text_size", (self.out.width, None)),
                      texture_size=lambda *_: setattr(self.out, "height", self.out.texture_size[1]))
        sv = ScrollView(); sv.add_widget(self.out); self.add_widget(sv)
        self.inp = TextInput(hint_text="Type here…", multiline=False, size_hint_y=None, height=48, font_name=FONT)
        self.inp.bind(on_text_validate=lambda *_: self.send())
        self.add_widget(self.inp)
        self.add_widget(Button(text="Send", size_hint_y=None, height=48, on_release=lambda *_: self.send()))

    def send(self):
        t = self.inp.text.strip()
        if not t:
            return
        self.inp.text = ""; self.out.text = "Thinking…"
        threading.Thread(target=self._call, args=(t,), daemon=True).start()

    def _call(self, text):
        try:
            r = requests.post(f"{SERVER}/api/chat", timeout=90,
                              data={"sid": self.sid, "lang": LANGS[self.lang.text], "text": text, "speak": "true"})
            j = r.json()
            if r.status_code != 200:
                raise RuntimeError(j.get("error", "server error"))
            msg = j["reply"]
            if j["checklist"]:
                msg += "\n\nKeep ready:\n- " + "\n- ".join(j["checklist"])
            Clock.schedule_once(lambda *_: setattr(self.out, "text", msg))
            if j.get("audio"):
                p = os.path.join(tempfile.gettempdir(), "reply.wav")
                open(p, "wb").write(base64.b64decode(j["audio"]))
                Clock.schedule_once(lambda *_: (SoundLoader.load(p) or type("N", (), {"play": lambda s: None})()).play())
        except Exception as e:
            Clock.schedule_once(lambda *_: setattr(self.out, "text", f"⚠️ {e}"))


class KaushalApp(App):
    def build(self):
        return Root()


if __name__ == "__main__":
    KaushalApp().run()
