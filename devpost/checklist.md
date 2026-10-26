---
doc: checklist
status: approved
---

# Build Checklist

Build mode: fast

## Slices

- [x] **1. Paste a prompt and see local redactions**
  Becomes usable: A locally running ContextGuard page accepts a prompt and shows a cleaned copy-ready result, redaction breakdown, character count, and total match count without making external calls.
  Why now: This delivers the unique local-first kernel before adding the external Gemini dependency. It also provides an early working page for visual and behavior feedback.
  PRD ref: `prd.md > The Core Journey`, `prd.md > Screens and Layout`, `prd.md > Local scan, masking, and results`, `prd.md > Prompt input and detector selection`, `prd.md > States and Boundaries`
  Spec ref: `spec.md > Components > app.py — Streamlit page and session flow`, `spec.md > Components > scanner.py — local detection, redaction, and Gemini analysis`, `spec.md > Components > .streamlit/config.toml — local appearance and telemetry`, `spec.md > Data Model`, `spec.md > File Structure`
  Build: Extend `.gitignore` to exclude `myvenv/`, `.venv/`, and Python caches while preserving credential/profile rules. Add the tested dependencies, blank `.env.example`, and local dark/telemetry config. Implement local detector rules, one-pass redaction/counts, and the matching Streamlit page states; add offline unit tests using synthetic data only. Do not wire a Gemini request in this slice.
  Verify (mechanical): Run `.\myvenv\Scripts\python.exe -m unittest discover -s tests`; start the app with `.\myvenv\Scripts\python.exe -m streamlit run app.py` and confirm the page responds at `http://localhost:8501` without console errors or network/external URLs. `.streamlit/config.toml` must bind the server to `127.0.0.1`.
  Learner check: Paste a clearly fake prompt containing a fake API-key pattern, an example email, and a labeled password. Confirm each appears as a redacted placeholder with correct counts, then change a detector and confirm old results disappear until rescanned.
  Commit: `Add local prompt scanning flow`

- [x] **2. Opt into Gemini for a validated context summary**
  Becomes usable: After reviewing local redactions, the user can explicitly enable Gemini and submit again to see a validated risk score, level, and two findings; local results remain available if Gemini cannot run.
  Why now: This adds the external service only after the local kernel is working and tested, so the privacy boundary and fallback can be verified independently.
  PRD ref: `prd.md > Optional Gemini Deep Context Analysis`, `prd.md > States and Boundaries`, `prd.md > Reset`
  Spec ref: `spec.md > Components > scanner.py — local detection, redaction, and Gemini analysis`, `spec.md > Components > app.py — Streamlit page and session flow`, `spec.md > External Services and Dependencies`, `spec.md > Important Failure Modes`
  Build: Add the Pydantic response schema and Google GenAI call using `gemini-3.5-flash-lite`; pass only the cleaned text. Add the masked sidebar key/.env fallback, explicit toggle-and-button gating, privacy-mode updates, structured-response UI, missing-key/API/timeout warnings, and toggle-off hiding behavior. Add mocked tests for request content and schema validation.
  Verify (mechanical): Run `.\myvenv\Scripts\python.exe -m unittest discover -s tests`; confirm tests prove no request is made by local scanning alone and that the mocked Gemini request contains only redacted text. Run the app without a key and verify local scanning remains usable with the missing-key warning; if a key is already configured locally, perform one opt-in smoke test without sharing the key. No live Gemini request was made because no key was configured.
  Learner check: Run a local-only scan, review its cleaned output, then enable Gemini and click **Scan & Mask Prompt** again. Confirm the status becomes Hybrid, the analysis appears only after that click, and switching Gemini off hides analysis while preserving local results.
  Commit: `Add opt-in Gemini context analysis`

## Hands-on Checkpoints

- [x] Early usable behavior explored — after slice 1, before Gemini integration; learner confirmed expected masking and stale-result clearing with no mismatches or UI issues
- [x] Final kick-the-tires exploration and feedback completed — learner confirmed the Hybrid toggle, no-key fallback, toggle-off behavior, and Reset; no changes requested

## Final Review

- [x] Final review complete — mechanical checks passed, no feedback changes were requested, and learner confirmed the proof of concept is ready for the hackathon showcase

## Code Tour and App Map

- [x] Learning activity complete — brief evidence-based recap; learner chose recap instead of an interactive code route
- [x] Optional edit and transfer reflection addressed — edit not applicable to recap; learner answered the optional transfer question
- [x] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: Brief recap connected the localhost-only privacy boundary to the initial smoke-test evidence; `.streamlit/config.toml` binds to `127.0.0.1`, and `tests/test_scanner.py` checks that only redacted text reaches the mocked Gemini request. All 14 tests pass; the no-key UI fallback was also verified.
Route and stops: Reference-only route in `devpost/app-map.html`: `app.py` scan button → `scanner.py` `scan_prompt()` / `analyze_with_gemini()` → `app.py` results. No interactive code route was completed.
Edit outcome: Not applicable; learner chose the brief recap rather than an optional code edit.
Reflection: Answered; personal response saved only in the ignored learner profile.
Activity mode: Brief recap.

## Revisions

- Bound Streamlit to `127.0.0.1` after the initial smoke test showed that its default configuration announced network and external URLs, conflicting with the local-only runtime.
