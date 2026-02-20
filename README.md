# OpenClaw Skills

Custom skills for [OpenClaw](https://github.com/openclaw/openclaw) — the autonomous agent framework.

## Skills

### 🎬 youtube-dl
Download YouTube videos and audio in highest quality.
- Auto-installs `yt-dlp` and `ffmpeg` if needed
- Downloads 4K/8K when available
- Extracts audio as MP3
- Embeds subtitles and metadata

**Created:** Feb 19, 2026

---

### 📧 gmail
Gmail integration via Maton API.
- Read/send emails
- Search inbox
- Manage labels

**Source:** ClawHub

---

### 💼 linkedin-api
LinkedIn integration via Maton API.
- Post updates
- Manage profile
- Run ad campaigns

**Source:** ClawHub

---

### ✍️ linkedin-writer
AI-powered LinkedIn post writing.
- Natural-sounding posts
- Story-driven content
- Avoids "content mill" tone

**Source:** ClawHub

## Installation

Install skills via ClawHub:

```bash
openclaw skills install youtube-dl
```

Or manually copy to your workspace:

```bash
cp -r youtube-dl ~/.openclaw/workspace/skills/
```

## License

See individual skill directories for license information.
