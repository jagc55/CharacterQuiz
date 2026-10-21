# CharacterQuiz: Automated Video Game Character Quiz for TikTok & YouTube Shorts

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/jagc55/CharacterQuiz)
[![Format](https://img.shields.io/badge/video%20format-9%3A16%20%281080x1920%29-purple.svg)](https://github.com/jagc55/CharacterQuiz)
[![Portfolio Case Study](https://img.shields.io/badge/Portfolio-Case%20Study%20%26%20Showcase-success.svg?logo=markdown)](PORTFOLIO.md)

*Translations: [English](README.md) | [Español](README_es.md) • Portfolio Case Study: [English](PORTFOLIO.md) | [Español](PORTFOLIO_es.md)*

**CharacterQuiz** is a fully automated, production-ready Python system designed to generate, schedule, and publish high-retention vertical videos (9:16, 1080x1920 @ 30 FPS) for **TikTok** and **YouTube Shorts**.

The format features an engaging, gamified video game trivia experience: an **introductory hook screen in English**, **cinematic gaming neon transitions**, **3 character rounds with progressive retro pixelation** (3 PTS → 2 PTS → 1 PT → Full HD Reveal), and an **interactive call-to-action outro screen** engineered to maximize watch time, comments, and subscriber growth.

---

## Output Directory (`Blurred_characters/`)

All generated `.mp4` video files and companion `.json` metadata are automatically saved into the root folder:
```
Blurred_characters/
├── quiz_20261021_145706_cloyster_pacman_raiden_mk.mp4
└── quiz_20261021_145706_cloyster_pacman_raiden_mk.json
```

Each generated video includes a companion `.json` file containing:
- Viral-optimized video title
- SEO description with trending hashtags (`#Shorts`, `#Gaming`, `#QuizGamer`, `#VideoGames`, etc.)
- List of characters, game franchises, and individual round breakdown
- Background asset name and social media upload status (YouTube & TikTok)

---

## Video Structure (50.5-Second High-Retention Format)

Every video is structured into 5 distinct phases engineered for maximum viewer retention and algorithmic completion rates (< 60s):

```
[Intro Screen: 2.5s] -> [Transition: 0.5s] -> [Round 1: 14.5s] -> [Round 2: 14.5s] -> [Round 3: 14.5s] -> [Transition: 0.5s] -> [Outro & CTA: 3.5s]
```

### 1. Intro Hook Screen (0.0s – 2.5s)
- **Top Badge:** `VIDEO GAME CHALLENGE`
- **Hook Question (100% English):**
 > **CAN YOU GUESS** 
 > **THE FOLLOWING** 
 > **VIDEO GAME CHARACTERS?**
- **3 Mystery Loot Boxes:** Visual preview of Round 1 (Gold), Round 2 (Cyan), and Round 3 (Magenta) with glowing `?` icons.
- **Rules & Stakes:** *"3 CHARACTERS • 9 POINTS MAX • Guess before the pixels fully clear! The faster you guess, the more points you get!"*
- **Algorithmic Engagement:** *"ARE YOU A TRUE GAMER? CAN YOU SCORE 9/9 POINTS?"*
- **Action Banner:** *"GET READY TO PLAY!"*

### 2. Cinematic Gaming Transitions (2x 0.5s)
- **Smooth Hermite Push Slide:** The previous screen slides off to the left while the incoming screen slides in dynamically from the right using cubic Hermite smoothstep easing.
- **Electric Neon Divider:** A luminous cyan and white laser beam separates the frames with soft multi-layer bloom and a subtle impact flash.
- **Synchronized Audio SFX:** Custom-synthesized cinematic whoosh sweep mixed directly into the audio track.
- **Identical Consistency:** The exact same transition effect is applied from **Intro -> Minigame** and from **Minigame -> Outro**.

### 3. Minigame Rounds (3x 14.5s per character = 43.5s)
| Time Window (per round) | Scoring Stage | Visual & Audio Experience |
| :--- | :--- | :--- |
| **0.0s – 4.0s** | **Phase 1: +3 POINTS** | Heavy retro pixelation (35px). Total mystery. Subtle clock tick-tock audio. Glowing gold HUD. |
| **4.0s – 8.0s** | **Phase 2: +2 POINTS** | Medium pixelation (18px). General silhouettes and distinctive color palettes emerge. Neon orange HUD. |
| **8.0s – 12.0s** | **Phase 3: +1 POINT** | Light pixelation (8px). Visual countdown ticker with ascending frequency audio beeps and magenta HUD. |
| **12.0s – 14.5s** | **Reveal: 0 POINTS** | **100% Crisp Full HD Reveal (0px)**. Traditional dual-bell alarm ring & victory fanfare. Banner: `IT'S [NAME]!` with game franchise. |

### 4. Interactive Outro Screen (47.0s – 50.5s)
- **Gamified Score Summary:** *"HOW MANY POINTS DID YOU GET? DID YOU GET ALL 9 POINTS?"*
- **Comment Callout:** *"Comment 1-9 below and challenge your friends!"*
- **Interaction Badges:** Antialiased vector icons for **LIKE**, **SHARE**, and **FOLLOW**.
- **Retention Teaser:** *"NEW VIDEO EVERY DAY!"*

---

## 1-Click Multi-Device Installation

To set up this project on any computer, server, or VPS:

### On Windows:
Simply double-click:
```
setup.bat
```
*(Or run in PowerShell: `powershell -ExecutionPolicy Bypass -File .\setup.ps1`)*

The installer automatically:
1. Detects and installs **Python 3.12** if not present (via `winget`).
2. Detects and installs **FFmpeg** if not present.
3. Creates the required folder tree (`Blurred_characters`, `assets`, `backgrounds`, `data`).
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

## CLI Usage & Commands

You can run commands directly from your terminal:

### 1. Generate 1 video (3 characters) immediately
```bash
python main.py --once
```
*Picks the next 3 unused characters in rotation from `data/characters.json` and renders the complete 50.5s video.*

### 2. Start automated mode (every 4 hours)
```bash
python main.py --schedule
```
*Generates an initial video right away, then schedules a new one every 4 hours indefinitely.*

### 3. Generate with specific characters
```bash
python main.py --character mario,sonic,kratos --once
```
*Combine any characters from the database of 210+ iconic gaming legends.*

### 4. Inspect character catalog and history
```bash
python main.py --list-characters
```

---

## Connecting YouTube Shorts & TikTok APIs

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
 cp .env.example .env # Linux / Mac
 copy .env.example .env # Windows
 ```
2. Insert your developer token under `TIKTOK_ACCESS_TOKEN`.

---

## Catalog of 210+ Verified Characters

The database in `data/characters.json` includes **210+ curated characters**:
- **73 Super Smash Bros Ultimate fighters** with direct high-resolution transparent renders.
- **50 Pokémon species** spanning multiple generations.
- **87 Multiplatform Gaming Icons** (Kratos, Master Chief, Solid Snake, Geralt of Rivia, Doom Slayer, Gordon Freeman, Lara Croft, Arthur Morgan, etc.).

If a local character image is not present in `assets/characters/`, the system automatically fetches the transparent HD render from Wikipedia or GitHub CDN!

---

## Project Structure

```
CharacterQuiz/
│
├── Blurred_characters/ # Output directory for generated MP4 videos and JSON metadata
├── backgrounds/ # 24+ dynamic gaming backdrops with auto-cover crop & vignette
├── assets/
│ ├── characters/ # PNG character portraits (transparent/high-res)
│ └── audio/
│ ├── bgm/ # Curated CC0 16-bit RPG & chiptune background tracks
│ └── sfx/ # Mechanical clock ticks, countdown beeps, alarm bells, whoosh
│
├── data/
│ ├── characters.json # Database of 210+ video game characters with games and tags
│ └── history.json # History log to prevent duplicate characters across cycles
│
├── src/
│ ├── config.py # Core configuration (1080x1920, 30 FPS, timing parameters)
│ ├── character_manager.py # Character rotation and Wikipedia / GitHub CDN downloader
│ ├── audio_engine.py # Procedural 44.1kHz stereo audio synthesizer & CC0 BGM mixer
│ ├── video_generator.py # Multi-stage pixelation, intro screen, transitions, HUD overlay & MoviePy 2.0 engine
│ ├── scheduler.py # 4-hour background scheduler loop
│ └── uploaders/
│ ├── youtube_uploader.py # YouTube Data API v3 integration (#Shorts)
│ ├── tiktok_uploader.py # TikTok Content Posting API v2 integration
│ └── manager.py # Upload dispatcher and status logger
│
├── .env.example # Environment variables template
├── requirements.txt # Python package dependencies
├── setup.bat / setup.ps1 # 1-click Windows installer
├── setup.sh # Linux / macOS installer
├── run.bat # Interactive Windows launcher
├── main.py # Main CLI entrypoint
├── PORTFOLIO.md # Full Portfolio Showcase & Technical Case Study (English)
├── PORTFOLIO_es.md # Presentación para Portfolio y Caso de Estudio (Español)
├── README.md # English documentation
└── README_es.md # Spanish documentation
```
