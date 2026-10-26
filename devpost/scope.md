---
doc: scope
status: approved
---

# ContextGuard

A local-first Streamlit app that redacts sensitive text before a user copies a prompt into an AI chatbot.

## The Unique Kernel
Explicit secrets and personal data are masked locally before anything can be sent to an AI service. A separate, off-by-default Gemini pass can look for contextual risks, but it receives only the already-redacted text.

## Who It's For
Developers, students, and professionals who copy code snippets or text into AI chatbots and want a quick check for exposed credentials or personal information before sending it.

## The Core Loop
The user pastes a prompt or code snippet, runs **Scan & Mask**, and reviews a cleaned version and security summary. The local scan works without Gemini; the user can explicitly opt into a deeper Gemini analysis of the redacted text.

## Inspiration & Identity
No visual references were shared. The app should feel lightweight, clear, and security-conscious, with an obvious local-only path and a plain-language disclosure beside the optional Gemini control.

## Why This Matters to the Learner
The learner wants to address the real-world risk of sensitive information accidentally entering public AI models, while learning to use AI tools to move quickly from an idea to a structured PRD, technical spec, and working app under hackathon deadlines.

## What "Working" Looks Like
In a short demo, a clearly fake prompt containing example credentials, an email, and a contextual risk is scanned. The local pass visibly replaces supported secrets and personal data with labeled placeholders. With the optional toggle left off, no Gemini call is made; with it enabled, only the redacted text is sent to Gemini and the app shows a contextual-risk summary. The app does not claim perfect detection or that all confidential content is automatically removed.

## The POC Boundary
- A locally run Streamlit app with a manual paste-and-scan flow.
- Local pattern-based detection and masking for the initial supported credential, password, email, and phone-number formats, including Google GenAI, OpenAI, and AWS key patterns.
- A cleaned prompt ready for the user to review and copy, plus a concise security audit summary.
- An optional Gemini contextual pass, off by default, with a clear disclosure; it receives only the locally redacted text.

## Later
- Broader detector coverage and tuning for false positives and missed patterns.
- Deployment or integrations beyond the manual paste-and-scan workflow, if there is time and a reason to pursue them.

## Explicitly Cut
- Sending the original prompt to Gemini; this conflicts with the local-first privacy boundary.
- Automatic interception or direct integration with AI chat services; manual review and copy are enough to demonstrate the core loop.
- A guarantee that every secret or contextual risk will be detected; the prototype can only report on its supported checks.
