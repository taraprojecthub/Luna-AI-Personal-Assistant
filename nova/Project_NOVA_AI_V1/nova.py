import os
import re
import tempfile
import subprocess
import webbrowser
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
CHAT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
TRANSCRIBE_MODEL = os.getenv("NOVA_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe").strip()
TTS_MODEL = os.getenv("NOVA_TTS_MODEL", "gpt-4o-mini-tts").strip()
TTS_VOICE = os.getenv("NOVA_TTS_VOICE", "marin").strip()
SAMPLE_RATE = 16000

if not API_KEY:
    raise SystemExit(
        "OPENAI_API_KEY is missing. Copy .env.example to .env and add your API key."
    )

client = OpenAI(api_key=API_KEY)
conversation = []
SYSTEM_PROMPT = """You are NOVA, a practical personal AI assistant running on a Windows PC.
Understand Sinhala, Singlish (Sinhala written with Latin letters), and English.
Reply in the language the user mainly used. Be concise, clear, and useful.
You cannot directly control the PC except for the explicitly allowlisted commands
handled by the local application. Never claim you performed an action unless the
application confirms it. Do not ask for or reveal API keys or passwords.
The spoken answer is AI-generated speech, not a human voice.
"""

def record_until_enter():
    frames = []

    def callback(indata, frame_count, time_info, status):
        if status:
            print(f"\nAudio note: {status}")
        frames.append(indata.copy())

    print("\n🎙️ Recording... Speak now. Press Enter to stop.")
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        callback=callback,
        blocksize=0,
    ):
        input()

    if not frames:
        raise RuntimeError("No audio captured. Check your microphone and Windows permissions.")

    audio = np.concatenate(frames, axis=0)
    if len(audio) < SAMPLE_RATE // 3:
        raise RuntimeError("Recording was too short. Please try again.")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        sf.write(temp_path, audio, SAMPLE_RATE, subtype="PCM_16")
        with open(temp_path, "rb") as audio_file:
            result = client.audio.transcriptions.create(
                model=TRANSCRIBE_MODEL,
                file=audio_file,
            )
        return result.text.strip()
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

def speak(text):
    if not text:
        return
    temp_path = None
    try:
        response = client.audio.speech.create(
            model=TTS_MODEL,
            voice=TTS_VOICE,
            input=text[:4000],
            response_format="wav",
            instructions="Speak clearly at a natural pace. Preserve the language and wording of the input.",
        )
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        response.stream_to_file(temp_path)
        audio, sample_rate = sf.read(temp_path, dtype="float32")
        sd.play(audio, sample_rate)
        sd.wait()
    except Exception as exc:
        print(f"🔈 Voice playback failed: {exc}")
        print("NOVA's reply is still available as text.")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

def run_local_command(text):
    """Only explicit, fixed, allowlisted actions are executed locally."""
    normalized = text.lower().strip()
    patterns = [
        (r"\b(open|launch|start)\s+(notepad|වෙලාවට notepad)\b", "notepad"),
        (r"\b(open|launch|start)\s+(calculator|calc)\b", "calculator"),
        (r"\b(open|launch|start)\s+(file explorer|explorer)\b", "explorer"),
    ]
    for pattern, action in patterns:
        if re.search(pattern, normalized):
            if action == "notepad":
                subprocess.Popen(["notepad.exe"])
                return "Opening Notepad."
            if action == "calculator":
                subprocess.Popen(["calc.exe"])
                return "Opening Calculator."
            if action == "explorer":
                subprocess.Popen(["explorer.exe"])
                return "Opening File Explorer."

    if re.search(r"\b(open|go to|visit)\s+(youtube|යූටියුබ්)\b", normalized):
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube in your default browser."

    if re.search(r"\b(open|show)\s+(downloads|download folder)\b", normalized):
        downloads = Path.home() / "Downloads"
        if downloads.exists():
            os.startfile(str(downloads))
            return "Opening your Downloads folder."
        return "I could not find your Downloads folder."

    if re.search(r"\b(exit|quit|shutdown nova|stop assistant)\b", normalized):
        return "__EXIT__"

    return None

def ask_ai(user_text):
    conversation.append({"role": "user", "content": user_text})
    # Keep a bounded recent conversation so prompts and costs do not grow forever.
    recent = conversation[-16:]
    response = client.responses.create(
        model=CHAT_MODEL,
        instructions=SYSTEM_PROMPT,
        input=recent,
    )
    answer = (response.output_text or "").strip()
    if not answer:
        answer = "I couldn't generate a response just now. Please try again."
    conversation.append({"role": "assistant", "content": answer})
    return answer

def main():
    print("=" * 52)
    print(" NOVA AI V1 — Windows voice assistant")
    print("=" * 52)
    print("Language: Sinhala / English / Singlish")
    print("Press Enter to record; press Enter again to stop.")
    print("Say 'open Notepad', 'open Calculator', 'open YouTube',")
    print("'open Downloads', or 'exit'.")
    print("Safety: NOVA only runs the fixed local commands listed above.")
    print("Note: API usage may incur charges.\n")

    while True:
        try:
            input("Press Enter when ready to speak (Ctrl+C to stop)...")
            transcript = record_until_enter()
            if not transcript:
                print("NOVA: I didn't catch any words. Try again.")
                continue

            print(f"\n🗣️ You: {transcript}")
            action_result = run_local_command(transcript)
            if action_result == "__EXIT__":
                print("NOVA: Goodbye!")
                speak("Goodbye!")
                break
            if action_result:
                print(f"🤖 NOVA: {action_result}")
                speak(action_result)
                continue

            answer = ask_ai(transcript)
            print(f"\n🤖 NOVA: {answer}\n")
            speak(answer)

        except KeyboardInterrupt:
            print("\nNOVA stopped.")
            break
        except Exception as exc:
            print(f"\n⚠️ Error: {exc}")
            print("Check your API key, internet connection, microphone, and API access.")

if __name__ == "__main__":
    main()
