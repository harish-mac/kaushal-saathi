# Kaushal Saathi 🛠️
**A voice assistant that explains government skilling schemes in your own language, and walks you through applying, one small step at a time.**

Built on the Sarvam Voice Agents platform, grounded in official PMKVY documents.

## The problem
Millions of Indians never use schemes they qualify for. The rules sit in long English PDFs, the portals assume digital confidence, and the people who need free training most (low literacy, first-time applicants, informal workers) are the ones least able to decode them. Fraud around "registration fees" makes it worse.

## The solution
Kaushal Saathi is a phone-style voice agent for **PMKVY (Pradhan Mantri Kaushal Vikas Yojana)**, the free skill training and certification scheme.

- 🗣️ **Speaks 11 languages.** Greets in English, asks which language you prefer, switches, and re-greets in that language.
- 🧭 **Finds your track.** Asks one question at a time (age, existing trade) and points you to Short Term Training or Recognition of Prior Learning (RPL).
- 🪜 **Guides step by step.** Asks "how do I register?" and gets one simple step, then "did you do it? next step?". Has an offline path (training centre / CSC) for people without a smartphone.
- 📚 **Answers only from the knowledge base.** Official PMKVY guidelines plus a plain-language how-to and glossary. If it doesn't know, it says so.
- 🛡️ **Protects people.** Reminds callers training is free, never asks for Aadhaar, OTP or bank details, and does not promise jobs or payments.

## Try it
1. Open the agent in Sarvam Voice Agents → **Test agent** (or the web widget link: _add link_).
2. Say nothing and listen to the English greeting.
3. Say "Hindi please", then "I am 35 and I am a tailor", then "How do I register?"

Full script and expected behaviour: [docs/demo.md](docs/demo.md)

## How it works
```
Caller (voice) → Sarvam Voice Agents (speech in, reasoning, speech out)
                    ├─ Instruction: persona, language rules, flow, safety
                    ├─ Tool: Change Output Language (language switch)
                    ├─ Tool: Query Knowledge Base → PMKVY knowledge base
                    └─ Tool: End Interaction
```
- [Agent overview](docs/agent-overview.md)
- [Conversation flow and safety rules](docs/conversation-flow.md)
- [Knowledge base](docs/knowledge-base.md)

## Optional companion: web demo
`web-demo/` is a small FastAPI website plus a Kivy client that call Sarvam APIs directly (Saaras v4 speech-to-text, Sarvam-105B, Mayura translation, Bulbul v3 voice, Sarvam Vision for turning PDFs into knowledge). It also serves `/llms.txt` from the same knowledge base. It is separate from the voice agent above and needs a Sarvam API key (see `web-demo/.env.example`). Offline logic tests are included; live API calls need your key.

## Limitations (honest list)
- Eligibility is **indicative**. The training centre has the final say.
- Facts come from official NSDC and PMKVY documents. PMKVY 4.0 was approved for 2022-23 to 2025-26, so check for extensions or a successor scheme before relying on it.
- Source websites disagree on age limits (15-45 vs 17-45 for training). The agent follows the NSDC FAQ (15-45 for short term training, 18-59 for RPL).
- On a phone call, links can only be spoken. The agent says them slowly and offers to repeat.
- Covers PMKVY in depth. Other schemes get only a light, clearly-labelled general explanation.

## Next steps
More schemes (PM-KISAN, Ayushman Bharat, Ujjwala), a training-centre locator tool, WhatsApp and IVR delivery, and SMS of the steps after the call.
