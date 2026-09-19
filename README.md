# 🎮 CharacterQuiz: Automated Video Game Character Quiz for TikTok & YouTube Shorts

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/jagc55/CharacterQuiz)
[![Format](https://img.shields.io/badge/video%20format-9%3A16%20%281080x1920%29-purple.svg)](https://github.com/jagc55/CharacterQuiz)

*Translations: [English](README.md) | [Español](README_es.md)*

**CharacterQuiz** is a fully automated Python system designed to generate, schedule, and publish high-retention vertical videos (9:16, 1080x1920) for **TikTok** and **YouTube Shorts**.

The format revolves around an engaging video game quiz: an iconic character starts heavily blurred and progressively clarifies across timed stages as clues and audio countdowns intensify, finishing with a crisp reveal and call-to-action to maximize viewer retention and comments.

---

## 📁 Output Directory (`Blurred_characters/`)

All generated `.mp4` video files and their corresponding `.json` metadata are automatically saved into the root folder:
```
Blurred_characters/
├── quiz_20260919_053421_kratos.mp4
├── quiz_20260919_053421_kratos.json
├── quiz_20260919_053919_mario.mp4
└── quiz_20260919_053919_mario.json
```

Each generated video includes a companion `.json` file with:
- Suggested viral title
- SEO description with trending hashtags (`#Shorts`, `#Gaming`, `#AdivinaElPersonaje`, etc.)
- Character and franchise details
- Social media publishing status

---

## ⏱️ Video Structure (13 Seconds, 9:16 Vertical)

| Time Window | Phase | Visual & Audio Dynamics |
| :--- | :--- | :--- |
| **0.0s – 3.5s** | **Phase 1: 100% Blur** | Total mystery. High Gaussian blur + radial ambient contrast spotlight. Clue 1: *"Can you recognize the colors?"*. Rising suspense synth beat. |
| **3.5s – 6.5s** | **Phase 2: 50% Blur** | Blur is halved. Basic silhouette and color blocking become visible. Clue 2: Key character trivia (debut year, franchise, or backstory). |
| **6.5s – 9.0s** | **Phase 3: 20% Blur** | Main features emerge. Dynamic on-screen countdown (`3... 2... 1...`) with ascending audio beeps and shrinking progress bar. |
| **9.0s – 13.0s** | **Phase 4: Crisp Reveal** | **0% Blur (Full HD clarity)**. Triumphant victory fanfare & sub-bass impact. Title banner: `>> IT'S [NAME]! <<` with franchise name and comment CTA. |

---

## 💻 1-Click Multi-Device Installation

To set up this project on another computer, server, or VPS:

### On Windows:
Simply double-click:
```
setup.bat
```
*(Or in PowerShell: `powershell -ExecutionPolicy Bypass -File .\setup.ps1`)*

The installer automatically:
1. Detects and installs **Python 3.12** if not present (via `winget`).
2. Detects and installs **FFmpeg** if not present.
3. Creates the required folder tree (`Blurred_characters`, `assets`, `data`).
4. Installs all packages from `requirements.txt`.
5. Creates the initial `.env` configuration file.

Once installed, you can launch everything via the interactive double-click launcher:
```
run.bat
```

### On Linux / macOS / VPS:
Run in your terminal:
```bash
chmod +x setup.sh
./setup.sh
```

---

## 🚀 CLI Usage & Commands

You can also run commands directly from your terminal:

### 1. Generate 1 test video immediately
```bash
python main.py --once
```
*Picks the next unused character in rotation from `data/characters.json` and renders the video.*

### 2. Start automated mode (every 4 hours)
```bash
python main.py --schedule
```
*Generates an initial video right away, then schedules a new one every 4 hours indefinitely.*

### 3. Generate a specific character
```bash
python main.py --character sonic --once
```
*Available IDs: `mario`, `sonic`, `kratos`, `master_chief`, `link`, `pikachu`, `pacman`, `cloud_strife`, `lara_croft`, `solid_snake`, `steve`, `crash_bandicoot`, `samus_aran`, `donkey_kong`, `geralt`, etc.*

### 4. Inspect character catalog and history
```bash
python main.py --list-characters
```

---

## ⚙️ Connecting YouTube Shorts & TikTok APIs

Videos are always rendered and safely stored in `Blurred_characters/`. When you are ready to enable direct auto-posting:

### YouTube Shorts:
1. Open [Google Cloud Console](https://console.cloud.google.com/) and create a project.
2. Enable the **YouTube Data API v3**.
3. Under *Credentials*, create an **OAuth 2.0 Client ID** (Application type: *Desktop app*).
4. Download the JSON credentials file and place it in the project root as `client_secret.json`.
5. On the first run with YouTube enabled, a browser window will open to authenticate your channel. The access token is saved to `youtube_token.json` for all future automated uploads.

### TikTok:
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env     # Linux / Mac
   copy .env.example .env   # Windows
   ```
2. Insert your developer token under `TIKTOK_ACCESS_TOKEN`.

---

## 🎨 Adding Custom Characters

To expand your catalog, simply add a new entry to `data/characters.json`:
```json
{
  "id": "shadow",
  "name": "Shadow the Hedgehog",
  "game": "Sonic / SEGA",
  "wiki_page": "Shadow_the_Hedgehog",
  "clues": [
    "Created by Dr. Gerald Robotnik as the Ultimate Life Form.",
    "Sonic's dark rival equipped with jet-skating hover shoes."
  ],
  "tags": ["#Shadow", "#Sonic", "#SEGA", "#Gaming", "#Shorts"]
}
```
If you don't provide a custom image at `assets/characters/shadow.png`, the system will automatically fetch the official high-resolution image from Wikipedia!

---

## 📂 Project Structure

```
CharacterQuiz/
│
├── Blurred_characters/            # Output directory for generated MP4 videos and JSON metadata
├── assets/
│   ├── characters/                # PNG character portraits (transparent/high-res)
│   └── audio/                     # Synthesized stereo audio (suspense, beeps, fanfare)
│
├── data/
│   ├── characters.json            # Database of 15+ video game characters with clues and tags
│   └── history.json               # History log to prevent duplicate characters across cycles
│
├── src/
│   ├── config.py                  # Core configuration (resolution, FPS, intervals, paths)
│   ├── character_manager.py       # Character rotation and Wikipedia thumbnail downloader
│   ├── audio_engine.py            # Procedural 44.1kHz stereo audio synthesizer
│   ├── video_generator.py         # Progressive blur video rendering engine
│   ├── scheduler.py               # 4-hour background scheduler loop
│   └── uploaders/
│       ├── youtube_uploader.py    # YouTube Data API v3 integration (#Shorts)
│       ├── tiktok_uploader.py     # TikTok Content Posting API v2 integration
│       └── manager.py             # Upload dispatcher and status logger
│
├── .env.example                   # Environment variables template
├── requirements.txt               # Python package dependencies
├── setup.bat / setup.ps1          # 1-click Windows installer
├── setup.sh                       # Linux / macOS installer
├── run.bat                        # Interactive Windows launcher
├── main.py                        # Main CLI entrypoint
├── README.md                      # English documentation
└── README_es.md                   # Spanish documentation
```
