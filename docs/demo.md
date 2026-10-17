# Live demo and testing

## Setup
1. Agent saved, knowledge base `pmkvy_agent` attached (Settings), Query Knowledge Base shows On (Tools → System tools).
2. In **Test agent**, start a **new session** so the current greeting is used.
3. Allow microphone access.

## Script
| # | Say | Expected |
|---|---|---|
| 1 | (nothing) | English greeting that lists the languages and asks for a preference |
| 2 | "Hindi please" | Switches to Hindi, short Hindi welcome |
| 3 | "I am 35 and I am a tailor" | Recommends RPL, explains the certificate simply |
| 4 | "How do I register?" | One step, then asks whether the caller can use the internet |
| 5 | "Is it free?" | Yes, plus a fraud warning |
| 6 | "I have no smartphone" | Training centre or CSC, and what to carry |
| 7 | "Tell me about [another scheme]" | Light general idea, marked unverified, no amounts, points to official site |

## Manual test log (team-run)
Run as one live conversation by the team:
- "Hindi please": passed. Switched on the first reply and welcomed warmly.
- "I am 35 and a tailor": passed. Stayed in Hindi throughout, asked "are you still working as a tailor?" once, then correctly recommended RPL with a simple certificate explanation.
- "How do I register?": passed. Gave one step (register on the Skill India portal), then offered the offline route.

_Replace this log with your own results and a date before submitting._

## Optional prompt fix: stop re-asking known facts
Add under ELIGIBILITY in the Instruction:
```
- Remember everything the caller has already told you (age, trade, language). Never ask again for a fact already given. If they say "I am a tailor", treat that as already working in a trade and only ask for what is still missing, for example age.
```

## Recording checklist
- [ ] 60 to 90 second screen recording showing greeting, language switch, RPL answer, one-step guidance
- [ ] Saved as `assets/demo-call.mp4`
- [ ] Screenshots of Instructions, Tools, Settings, Knowledge base saved in `assets/screenshots/`
