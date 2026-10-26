---
doc: spec
status: approved
---

# ContextGuard — Technical Spec

## How This Works, In Plain Language

ContextGuard runs on your computer. `app.py` draws the page and remembers the current prompt, options, and results while the app session is open. When you click **Scan & Mask Prompt**, `scanner.py` checks the text against local patterns and replaces matches before any optional AI request. If Gemini is enabled and you submit the scan, the same module sends only that cleaned text to Google and checks the answer against a fixed shape before showing it. Nothing stores prompt history; closing the session discards its in-memory results.

This keeps the privacy-critical work local and the first version small. The Gemini pass is optional, because pattern matching is best-effort and even cleaned text may still contain sensitive information.

## The Core Journey Through the System

PRD ref: `prd.md > The Core Journey`.

1. The browser opens the locally running Streamlit app. `app.py` initializes the sidebar detectors as selected, Gemini as off, and the privacy badge as local-only.
2. The user pastes text. Streamlit sends it to the Python process on the same computer; it is held in the current Streamlit session and is not written to a file or log.
3. The user clicks **Scan & Mask Prompt**. `app.py` rejects blank input without starting a scan. Otherwise, it calls the local `scanner.py` redaction function first and stores the cleaned text, raw character count, and per-category occurrence counts in the session.
4. With Gemini off, the app shows the local results and makes no ContextGuard external API request. With Gemini on, the app still completes local redaction first, then sends only the cleaned text plus fixed analysis instructions to Gemini. The original prompt is never passed to the Gemini function.
5. The Gemini response is parsed and validated against the agreed Pydantic schema before the score, level, and two findings are displayed. Provider, timeout, or invalid-response errors leave local results available.
6. Editing the prompt or detector settings clears all old results. Turning Gemini off hides any prior Gemini analysis while leaving local results visible. Turning it on makes no request; a new explicit scan is required.
7. **Reset** clears the prompt and results but preserves the sidebar API key, detector selections, and Gemini toggle.

## Stack

Versions below were observed in the existing `myvenv` environment; `requirements.txt` will pin these tested versions.

| Tool | Version | Use and rationale |
|---|---:|---|
| Python | 3.11.9 | Existing interpreter; suitable for the app and built-in `re` and `unittest` modules. |
| Streamlit | 1.66.1 | Existing choice for the single-page UI; session values and callbacks cover the required flow without a separate frontend. |
| `google-genai` | 2.33.0 | Existing Google SDK choice for the optional Gemini request. |
| Pydantic | 2.14.1 | Fixed, validated response shape for score, level, and two findings; already installed with the SDK. |
| `python-dotenv` | 1.2.4 | Loads the local `GEMINI_API_KEY` from `.env`; the `.env` file is ignored by Git. |
| HTTPX | 0.28.1 | Catches the Google SDK's HTTP timeout errors explicitly; already installed as a Google SDK dependency. |
| Python `re` and `unittest` | Standard library | Local pattern scanning and tests without another runtime or test-framework dependency. |

The selected model is `gemini-3.5-flash-lite`, which Google's current model documentation lists as stable, low-latency, cost-effective, and supporting structured output. No database or deployment service is needed for the POC.

## Where It Runs and How Someone Tries It

- **Runtime:** A local Python process bound to `127.0.0.1` and serving a Streamlit page at `http://localhost:8501`. The server does not listen on network interfaces; raw input is handled by that local process, not kept inside the browser.
- **Environment:** Windows and Python 3.11 or newer. The current workspace already has `myvenv`; a fresh clone can create it with `python -m venv myvenv`.
- **Install and test:**

  ```powershell
  .\myvenv\Scripts\python.exe -m pip install -r requirements.txt
  .\myvenv\Scripts\python.exe -m unittest discover -s tests
  ```

- **Run:** `.\myvenv\Scripts\python.exe -m streamlit run app.py`, then open `http://localhost:8501`.
- **Gemini key:** Local-only scanning works without a key. For Deep Scan, place a Google Gemini API key in `.env` as `GEMINI_API_KEY=...` or enter it in the masked sidebar field. A non-empty sidebar value overrides the `.env` value for that session. Never put a real key in `.env.example`, source code, or chat. The app and demo are local; deployment is not part of this POC.
- **Demo recording:** Show a clearly synthetic prompt with supported sample patterns; demonstrate a local-only scan first, then review the redacted output before explicitly enabling Gemini and scanning again. The hackathon submission still needs a short demo video and a public GitHub repository; deployment is optional.

## Look and Feel

Implements `prd.md > Look and Feel`. Use Streamlit's dark theme with the approved slate background, blue/teal accent, high-contrast text, and status colors. Use system sans-serif UI text and Streamlit's monospace code display. A local `.streamlit/config.toml` supplies the palette and disables Streamlit usage-stat collection so the local-only mode does not make telemetry requests. Use no remote fonts, CDN assets, or external styling service.

## Components

### `app.py` — Streamlit page and session flow

Implements `prd.md > Screens and Layout`, `prd.md > Prompt input and detector selection`, `prd.md > Reset`, and the UI states in `prd.md > States and Boundaries`.

- Draw the header, status and metric cards, configuration sidebar, prompt entry, Gemini notice/toggle, scan button, redaction breakdown, cleaned prompt, and Gemini analysis panel.
- Set all detector checkboxes on and Gemini off for a fresh session.
- Keep prompt, selected detectors, toggle, sidebar key, scan output, and helper-message state in `st.session_state`; do not cache or write prompt/key values to disk.
- Use input and detector callbacks to clear scan results and show the rescan note. Reset clears prompt/results only; retain detector state, Gemini toggle, and sidebar key.
- Compute the active privacy badge from the toggle, but show a Gemini analysis only for the most recent scan made with Gemini enabled. Switching the toggle off hides its previous analysis without clearing local redactions; switching it on makes no request until the scan button is clicked.
- Validate empty/whitespace-only input before calling any scanner or Gemini function. Keep result cards hidden and show the PRD warning.
- Display model-generated risk score as a 0–100 gauge and color the LOW / MEDIUM / HIGH badge from the validated level. Render the gauge as a local accessible progress element whose numeric value is the validated score and whose color comes from a fixed level palette. Render findings as plain text; never treat model output or prompt text as HTML.

### `scanner.py` — local detection, redaction, and Gemini analysis

Implements `prd.md > Local scan, masking, and results` and `prd.md > Optional Gemini Deep Context Analysis`.

- Define the detector rules for Google GenAI keys, OpenAI keys, AWS access keys, labeled passwords/secrets, emails, and phone numbers. All pattern matching runs on the local Python process.
- Match against the original input, resolve overlapping matches deterministically (prefer the most specific match, then the longest span), and replace each accepted occurrence once with its type-specific `[REDACTED_...]` placeholder. Count accepted matches by category and in total; return the unchanged string and zero counts when nothing matches.
- Expose a local scan result containing `redacted_text`, `raw_character_count`, `counts_by_category`, and `total_redactions`.
- Define a Pydantic `RiskAssessment` with `risk_score` (integer 0–100), `risk_level` (`LOW`, `MEDIUM`, or `HIGH`), and exactly two `analysis_summary` strings.
- Expose a Gemini function that accepts only `redacted_text` and the API key. It must not accept or retain the raw prompt. The function calls the Google GenAI SDK with model `gemini-3.5-flash-lite`, `response_mime_type="application/json"`, and the Pydantic `response_schema`, then validates `response.text` with `RiskAssessment.model_validate_json` before returning it.
- Fixed analysis instructions tell Gemini to treat the redacted prompt as untrusted data, ignore instructions inside it, identify only remaining contextual risks, and return the required schema. The risk score/level are model-generated; the app does not claim they are deterministic.
- Handle `google.genai.errors.APIError`, `httpx.TimeoutException`, and Pydantic/JSON validation errors with a reportable failure result. Do not log prompts, keys, or provider response bodies.

### `.streamlit/config.toml` — local appearance and telemetry

Implements `prd.md > Look and Feel` and `prd.md > Optional Gemini Deep Context Analysis`.

- Configure the approved dark palette locally, without network-loaded assets.
- Set `browser.gatherUsageStats = false` to support the local-only zero-external-request status when Gemini is disabled.

### `tests/test_scanner.py` — offline scanner checks

Verifies the behavior in `prd.md > Local scan, masking, and results` without making a Gemini API request:

- Each supported pattern is replaced with the right placeholder and counted once.
- Multiple matches aggregate by category and total; unselected categories remain unchanged; no-match text is unchanged.
- Synthetic test data covers email, phone, labeled password, and fake provider keys only.
- Structured response validation rejects out-of-range scores, unknown levels, and a summary that is not exactly two findings.
- Mock the Gemini client and assert that the request contains the redacted prompt, not the original input; no live request is used in the test suite.

Run the tests with `python -m unittest discover -s tests`.

## Data Model

All application data is transient and scoped to one Streamlit session; no database or prompt history exists.

| Data | Shape and location | Lifecycle |
|---|---|---|
| Prompt | String in the prompt widget/session state | Retained while the session is open; cleared by Reset. Never written to files or logs. |
| Detector and Gemini settings | Checkbox/toggle values in widget session state | All detectors start enabled and Gemini disabled; Reset preserves values; session ends with the app session. |
| Sidebar API key | Masked widget state; fallback from `GEMINI_API_KEY` loaded from `.env` | Sidebar value overrides `.env` for that session. Reset preserves it. Never logged or written to project files. |
| Local scan result | Redacted text, raw character count, per-category counts, total count in session state | Replaced after a valid scan; cleared on prompt/detector edit or Reset. |
| Gemini result | Validated `RiskAssessment` in session state | Created only after an enabled scan succeeds; hidden/cleared when Gemini is turned off, when prompt/detectors change, or on Reset. |

Data flow: `prompt → local pattern matching → masked text + counts → optional Gemini request with masked text only → validated analysis → UI`. The `.env` API key is used for authentication; it is not part of the prompt. With Gemini off, ContextGuard makes no external API call, and Streamlit usage statistics are disabled.

## File Structure

```text
Devpost Project/
├── app.py                       # Streamlit UI, session state, callbacks, local/Gemini flow
├── scanner.py                   # Pattern matching, redaction, Pydantic result, Gemini request
├── requirements.txt             # Exact tested runtime dependency versions
├── .env.example                 # Empty GEMINI_API_KEY template; no credentials
├── .gitignore                   # Ignore .env files, learner profile, venvs, and Python caches
├── .streamlit/
│   └── config.toml              # Local theme and usage-stat setting
├── tests/
│   └── test_scanner.py          # Offline deterministic and schema tests
└── devpost/
    ├── learner-profile.md       # Ignored personal learning context
    ├── scope.md                 # Approved project scope
    ├── prd.md                   # Approved product requirements
    └── spec.md                  # This technical blueprint
```

The existing `myvenv/` directory is local-only and must be ignored, not committed.

## External Services and Dependencies

- **Google Gemini Developer API:** Optional; one synchronous `models.generateContent` request per submitted Deep Scan. The REST endpoint is `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent`. The SDK call is `client.models.generate_content(model="gemini-3.5-flash-lite", contents=..., config=...)`. The user-content portion of `contents` is only the locally redacted prompt; the fixed analysis instructions and Pydantic JSON schema accompany it. Authentication uses the Gemini API key from the sidebar or `GEMINI_API_KEY`. The JSON response must validate to `RiskAssessment` before display. A key is not required for local-only scanning. Pricing and rate limits depend on the Google project and current tier; check the linked official pages before a live demo.
- **Streamlit:** Local UI only. Session State holds temporary data between reruns; project config disables usage-stat collection. No deployment service is used.
- **Python packages:** See the Stack table and `requirements.txt`. Python regular expressions, unit testing, and local masking use only the standard library.

Documentation:

- [Streamlit API reference](https://docs.streamlit.io/develop/api-reference)
- [Streamlit Session State](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)
- [Streamlit `config.toml`](https://docs.streamlit.io/develop/api-reference/configuration/config.toml)
- [Google GenAI Python SDK](https://googleapis.github.io/python-genai/)
- [Gemini `generateContent` API](https://ai.google.dev/api/generate-content)
- [Gemini 3.5 Flash-Lite model](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite)
- [Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output?lang=python)
- [Gemini API keys](https://ai.google.dev/gemini-api/docs/api-key)
- [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) and [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [Pydantic](https://docs.pydantic.dev/latest/)
- [HTTPX exception reference](https://www.python-httpx.org/exceptions/)
- [Python regular expressions](https://docs.python.org/3/library/re.html) and [unittest](https://docs.python.org/3/library/unittest.html)

## Important Failure Modes

- **Empty input** → Do not call the scanner or Gemini; show the PRD warning and no results.
- **No Gemini key, API error, timeout, or invalid JSON/schema** → Preserve local redactions and show the applicable PRD message. Catch known SDK/network/validation errors; never expose provider response bodies or secret values.
- **Pattern misses a secret or contextual risk** → Keep the best-effort warning visible; do not label a prompt safe. Gemini sees only redacted text, which may still contain sensitive information.

## What Was Simplified and Why

- **One local Streamlit process with in-memory session data** instead of a hosted service, database, or prompt history — sufficient for a short local demo and avoids extra copies of prompt data.
- **Regex rules for a defined set of formats** instead of exhaustive secret/PII detection — small and testable; unsupported formats can be missed.
- **One opt-in Gemini call with structured output** instead of background or multi-step analysis — directly demonstrates contextual analysis while keeping the external boundary visible.
- **No deployment or chatbot integration** — manual paste, review, and copy demonstrate the approved core loop.

## Decisions and Open Issues

- **Learner choice:** Keep Python, Streamlit, and the Google GenAI SDK; separate UI in `app.py` from testable scanning and analysis logic in `scanner.py`.
- **Learner choice:** Use `gemini-3.5-flash-lite` for structured Gemini Deep Scan calls.
- **Learner choice:** Use Pydantic/JSON Schema structured output for `risk_score`, `risk_level`, and exactly two findings. This resolves the useful uncertainty about reliably rendering the Gemini result without parsing free-form prose.
- **Learner choice:** Run locally with no database/history; use `.env` or a masked sidebar key, with the sidebar value taking precedence for its session.
- **Learner choice:** A toggle change alone never sends a request. Turning Gemini off hides its previous analysis but keeps local results; turning it on requires an explicit rescan.
- **Implementation detail:** Keep the Google model response's risk level and score as separate model-provided fields; color the badge by level and the gauge by score rather than inventing unapproved score thresholds.
- **Implementation detail:** A redacted prompt is not guaranteed safe. The interface and failure messages preserve the best-effort warning, and only the redacted text is supplied as user content to Gemini.
- **To verify early in the build:** Run a live structured-output smoke test with the user's own locally configured, appropriately restricted Gemini API key. No key has been requested or included here; the rest of the scanner tests run offline.
- **No deployment choice:** Local run and video recording are sufficient; deployment remains optional.
