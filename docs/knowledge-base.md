# Knowledge base

Name in Sarvam Voice Agents: `pmkvy_agent`. Attached to the agent in **Settings → Knowledge bases**, which switches on the **Query Knowledge Base** tool.

## Contents
| File | Purpose |
|---|---|
| `pmkvy_core.md` | Curated facts: components, eligibility, ages, documents, how to apply, cost, certificate |
| `pmkvy_howto_simple.md` | Plain-language explanation, glossary, 9-step registration guide, offline path, safety tips, common questions |
| `PMKVY-4.0-Guidelines_final-copy-2.pdf` | Official scheme guidelines |
| Two further official PDFs (add titles here) | Supporting scheme documents |
| `pmkvy-proposal-user-manual.pdf` | Manual for training partners applying to run PMKVY, not for candidates |

Source copies of the two markdown files are in `web-demo/kb/`.

## How it prevents wrong answers
1. The instruction says PMKVY facts must come from the knowledge base and must never be guessed.
2. If nothing is found, the agent says it is not sure and points to the nearest training centre or official website.
3. For other schemes it gives only a general idea, labelled unverified, with no amounts, dates or eligibility.
4. Links must appear in the knowledge base. The agent never invents a website.
5. Retrieval was checked with the console's **Test retrieval** box (age limit, registration steps, meaning of RPL).

## Known data issues
- Websites disagree on age limits. The NSDC FAQ gives 15-45 (training) and 18-59 (RPL), which is used here.
- PMKVY 4.0 covered 2022-23 to 2025-26. Check for extensions or a successor scheme.
- The training-partner manual can pull answers toward provider-side rules. Remove it if that happens in testing.
- Verify the three official links in `pmkvy_howto_simple.md` open correctly before a demo.

## Updating
Upload a new file in the console and it becomes searchable after processing. No retraining is involved.
