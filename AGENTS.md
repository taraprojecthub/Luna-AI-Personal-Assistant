# LUNA — Codex project instructions

You are working on LUNA, a personal Windows AI voice assistant with a hybrid local/cloud AI architecture.

## Product goals
- Windows-first desktop assistant.
- Sinhala, English, and Singlish-friendly conversation where the selected models support it.
- Local-first text reasoning through Ollama, with optional OpenAI cloud fallback.
- Push-to-talk voice input, configurable transcription, spoken replies.
- Safe, explicitly allowlisted Windows actions.
- Keep the app modular so wake-word detection, persistent memory, and smart-home integrations can be added later.

## Engineering rules
- Python 3.11+ recommended. Keep Windows support as the primary target.
- Never execute arbitrary model-generated shell commands.
- Tools must be implemented as fixed, validated functions with explicit confirmation for consequential actions.
- Bind the local web server to 127.0.0.1 by default. Do not expose it to a LAN or the public internet.
- Never log API keys or raw audio. Never commit `.env`.
- Keep local and cloud model providers behind a small provider interface.
- Add tests for parsing, tool routing, and safety-sensitive behavior.
- Be transparent when an operation requires an API key, internet, or a local Ollama model.
- Do not claim a feature works without testing it.
- Prefer small, reviewable changes. Explain files changed and give Windows commands to run tests.
