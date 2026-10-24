# Project NOVA AI V1 — Windows

A starter Sinhala/English voice assistant for Windows. This first version uses push-to-talk, OpenAI speech transcription, an OpenAI text model, speech synthesis, and a small allowlist of local PC actions.

## Requirements

- Windows 10 or Windows 11
- Python 3.11+ (Python 3.13 may work; if an audio dependency fails, try Python 3.12)
- A microphone and speakers/headphones
- An OpenAI API key with billing/API access enabled

## Install

Open Command Prompt in this folder:

```bat
py -m venv .venv
.venv\Scripts\activate
py -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
notepad .env
```

Put your API key in `.env`, replacing `replace_with_your_api_key`. Do not share the key or upload `.env` to GitHub.

## Run

```bat
py nova.py
```

Press Enter, speak, then press Enter again to stop recording. NOVA transcribes the recording, responds, and speaks the response.

## Initial allowlisted commands

- Open Notepad
- Open Calculator
- Open File Explorer
- Open YouTube
- Open Downloads
- Exit / quit NOVA

Only these fixed actions are executed locally. Arbitrary shell commands are not executed.

## Notes and limitations

- The first version is push-to-talk, not always listening. Wake-word support is a later milestone.
- Speech transcription and text-to-speech calls use the API and may incur charges.
- TTS voices are optimized for English; test Sinhala pronunciation on your own machine before deciding whether to use a separate Sinhala TTS engine.
- Keep API keys private. Do not commit `.env` to source control.
- The app sends recorded audio to the configured API provider for transcription.
- This is a starter project, not a production-grade always-on assistant.
