---
doc: prd
status: approved
---

# ContextGuard — Product Requirements

A local-first prompt checker for developers, students, and professionals who want to review and redact sensitive text before using an AI chatbot.
Source: `scope.md > Who It's For`, `scope.md > The Unique Kernel`.

## The Core Journey

1. The user opens ContextGuard and sees the single-page scanner, its privacy mode, and detector controls.
2. They paste a prompt or code snippet. All supported detectors are selected by default.
3. They select **Scan & Mask Prompt** with Gemini off by default. The local scan presents the cleaned prompt and redaction results without a Gemini call.
4. They review the cleaned prompt. If they want contextual analysis, they enable the Gemini toggle after reading the notice and select **Scan & Mask Prompt** again. Enabling the toggle alone never sends a request.
5. If Gemini is enabled and available for that scan, the app shows a contextual risk score, level, and two-bullet analysis based only on the redacted text. Otherwise, the local output remains available to review and copy.
6. The user checks the cleaned prompt before copying it into an AI chatbot. If they edit the prompt or detector selections, prior results are cleared until they scan again.

Source: `scope.md > The Core Loop`, `scope.md > What "Working" Looks Like`, `scope.md > The POC Boundary`.

## Screens and Layout

ContextGuard uses one page with a header, a narrow configuration sidebar, and a main scan-and-results area.

- **Header:** “🛡️ ContextGuard - AI Prompt Security” with the subtitle “Local-First Privacy Guard for Generative AI”.
- **Status and metrics:** A privacy-mode card reflects whether Gemini is off or enabled. After a valid scan, show total input characters and total redacted occurrences.
- **Sidebar:** A masked Gemini API key field; checkboxes for Google GenAI keys, OpenAI and AWS keys, passwords/secrets, email addresses, and phone numbers/PII; and a **Reset** button.
- **Main input area:** A large prompt/code input labeled “Paste your AI Prompt or Code Snippet here”, the Gemini disclosure and off-by-default toggle, and the **🛡️ Scan & Mask Prompt** button.
- **Results area:** Hidden until a valid scan. After a scan, show a redaction breakdown on the left and the cleaned prompt in a syntax-highlighted, copy-ready area on the right. When Gemini analysis is enabled and completed, show its risk gauge, risk-level badge, and two-bullet summary below or alongside the results.

## Look and Feel

Use a sleek, high-trust, lightweight cybersecurity look inspired by dark Linear or Vercel interfaces. Use deep slate/charcoal backgrounds (`#0F172A`, `#1E293B`), high-contrast white text, and blue/teal accents (`#0EA5E9`, `#14B8A6`). Use red (`#EF4444`) for redactions and high risk, green (`#10B981`) for safe/low-risk states, and yellow (`#F59E0B`) for medium risk. Use a clean sans-serif for interface text and monospace for prompts and code.

## Features and Behavior

### Prompt input and detector selection

- The input accepts a prompt or code snippet as plain text.
- On a new session, all supported detector checkboxes are selected. Users may uncheck individual categories.
- Total Characters is the character count of the raw input at the time of the most recent valid scan.
- Changing the input or any detector selection after a scan immediately clears/hides that scan's results and displays: “✏️ Input or detector settings modified. Click '🛡️ Scan & Mask Prompt' again to update results.”

Source: `scope.md > The Core Loop`, `scope.md > The POC Boundary`.

### Local scan, masking, and results

- Selecting **🛡️ Scan & Mask Prompt** runs the selected pattern-based detectors locally before any optional Gemini request.
- Supported categories are Google GenAI keys; OpenAI and AWS keys; labeled passwords/secrets; email addresses; and phone numbers/PII.
- Each match is replaced with a type-specific placeholder (for example, `[REDACTED_API_KEY]` or `[REDACTED_EMAIL]`). The original prompt is not displayed in the results.
- The redaction breakdown shows occurrence counts by category. Secrets Masked Count is the total number of redacted occurrences across all categories, not the number of categories.
- Show the cleaned prompt in a copy-ready area. If the scan has no matches, show the unchanged prompt and clearly report zero redactions; do not imply it is guaranteed safe.
- The privacy status reflects the selected mode: “🔒 Mode: 100% Local Regex Scan (Zero External Network Calls)” when Gemini is off, and “🛡️ Mode: Hybrid (Local Redaction + Gemini Context Analysis)” when the toggle is on. The Gemini result area separately shows whether analysis completed.

Source: `scope.md > The Unique Kernel`, `scope.md > What "Working" Looks Like`, `scope.md > The POC Boundary`.

### Optional Gemini Deep Context Analysis

- The “Enable Gemini Deep Context Analysis” toggle is off by default.
- Display this disclosure beside the toggle: “⚠️ Local regex redaction is pattern-based and best-effort. When enabled, ContextGuard sends only the redacted prompt to Google Gemini; unsupported secrets or other sensitive details may remain. Review the redacted prompt before enabling Deep Scan.”
- Changing the toggle alone never sends text to Gemini. A Gemini request occurs only after the user explicitly submits **Scan & Mask Prompt** with the toggle enabled.
- When enabled, Gemini receives only the locally redacted text; the original prompt is never sent to Gemini. The score and findings are model-generated and do not guarantee that all contextual risks are found.
- A completed analysis displays a color-coded 0–100 risk gauge, a LOW / MEDIUM / HIGH label, and a two-bullet contextual leak summary.
- If the toggle is off, no Gemini call is made.
- Turning the toggle off after an analysis hides the previous Gemini result but keeps local redactions visible. Turning it on does not make a request; the user must submit **Scan & Mask Prompt** again.
- The Gemini API key can come from the local `.env` configuration or the masked sidebar field. The sidebar key remains intact when Reset is used.

Source: `scope.md > The Unique Kernel`, `scope.md > The Core Loop`, `scope.md > The POC Boundary`.

### Reset

Selecting **Reset** clears the prompt, scan results, redaction breakdown, cleaned prompt, count metrics, Gemini score, and analysis summary. It preserves the Gemini API key, detector selections, and Gemini toggle state.

Source: `scope.md > The Core Loop`.

## States and Boundaries

- **First open:** Show the header, privacy mode, input, disclosure, toggle (off), and all detector checkboxes selected. Hide scan results and count metrics until a valid scan.
- **Empty or whitespace-only input:** Do not run a local scan or call Gemini. Show “⚠️ Please enter or paste a prompt or code snippet before running the scan.” below the input; keep results and count metrics hidden.
- **Valid scan with matches:** Show the cleaned prompt, category counts, total redacted occurrence count, raw-input character count, and the current privacy mode.
- **Valid scan without matches:** Show the unchanged prompt and zero redactions with a clear note that supported patterns found no matches; do not label the prompt safe.
- **Gemini disabled:** Complete the local scan without a Gemini call; display local-only mode. If the toggle is turned off after an analysis, hide the Gemini result but keep local results visible.
- **Gemini enabled, API key missing:** Keep local results usable and show: “⚠️ Gemini Deep Scan is enabled, but no Google Gemini API Key was found in your .env or sidebar. Please enter your API key to enable context analysis, or copy your locally redacted prompt above.”
- **Gemini request fails or times out:** Keep local results usable and show: “⚠️ Gemini contextual analysis could not be completed (Network/API Error). Your locally redacted prompt remains available to review and copy.”
- **Input or detector settings edited after a scan:** Immediately hide old metrics and results until the user scans again; show the rescan helper note.
- **Reset:** Clear input and all scan output and count metrics; preserve API key, detector selections, and toggle.

## Product Decisions

- The core scan is local-first; Gemini is a separate opt-in and receives only text after local masking.
- Gemini is off by default. The interface distinguishes Local and Hybrid modes and discloses best-effort limitations.
- Every supported detector starts selected; detector selections can be changed for a test.
- Local results are independent of Gemini availability. Missing credentials or a failed request must not block redaction output.
- Reset preserves configuration so a user can quickly run another test.
- The app is a manually operated proof of concept, not an automatic chatbot interceptor or a guarantee of complete secret detection.

## What We're Building

- One scanner page with the specified header, privacy status, input, detector controls, Gemini opt-in, results, and Reset behavior.
- Local pattern-based detection and redaction for the supported categories, with per-category and total occurrence counts.
- A copy-ready cleaned prompt and clear local-only status.
- Optional Gemini contextual analysis of redacted text, with transparent consent, a risk display, and resilient fallback behavior.
- Empty-input, no-match, edited-input, missing-key, request-failure, and reset states described above.

## Deferred From the POC

- Automatic integration with AI chat services; the user manually reviews and copies the cleaned prompt.
- Broader detector coverage and extensive false-positive or missed-pattern tuning; this POC supports only its named patterns.
- Deployment or other integrations; a locally run demo is sufficient for the proof of concept.

## Possible Later Enhancements

Improve detector coverage and tuning based on safe, clearly synthetic test prompts. Consider deployment or integrations only if they serve a later user need and have an explicit privacy model.

## Non-Goals

- Sending unredacted input to Gemini.
- Claiming that a prompt is completely safe or that every secret or contextual risk is detected.
- Persisting prompt history or adding user accounts.
- Automatically submitting prompts to another AI service.

## Open Questions

No unresolved product decisions block the technical spec. The exact detector patterns, Gemini response handling, and implementation details belong in `4-spec`; detector results remain best-effort.
