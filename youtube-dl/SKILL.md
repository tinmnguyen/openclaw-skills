---
name: youtube-dl
description: |
  Download YouTube videos and audio using yt-dlp with automatic highest quality selection.
  Use when the user wants to:
  - Download a YouTube video in highest quality
  - Extract audio from YouTube videos (MP3)
  - Get video info/metadata from YouTube
  - List available formats/qualities for a video
  - Download YouTube playlists or channels
  
  Auto-installs yt-dlp and ffmpeg if not present. Downloads to ~/Downloads/youtube by default.
---

# YouTube Downloader

Download YouTube videos and audio using yt-dlp. Automatically selects highest quality and installs required dependencies.

## Features

- ✅ **Auto-installs** yt-dlp and ffmpeg if not present
- ✅ **Highest quality** video downloads (4K/8K when available)
- ✅ **Automatic merging** of separate audio/video streams
- ✅ **Download videos** (MP4 with H.264/VP9)
- ✅ **Extract audio** (MP3 320kbps)
- ✅ **Get video info** (title, views, duration, best quality available)
- ✅ **List formats** (see all available qualities)
- ✅ **Playlist support**
- ✅ **YouTube Music support**
- ✅ **Subtitles** embedded when available

## Usage

### Download a Video (Highest Quality)

```python
exec: python3 skills/youtube-dl/scripts/youtube-dl.py download "https://www.youtube.com/watch?v=VIDEO_ID"
```

Downloads best available quality (up to 4K/8K) and automatically merges audio/video if needed.

### Download Audio Only (MP3)

```python
exec: python3 skills/youtube-dl/scripts/youtube-dl.py download "https://www.youtube.com/watch?v=VIDEO_ID" --audio
```

### Download to Custom Location

```python
exec: python3 skills/youtube-dl/scripts/youtube-dl.py download "https://www.youtube.com/watch?v=VIDEO_ID" --output "/path/to/folder"
```

### Get Video Info

```python
exec: python3 skills/youtube-dl/scripts/youtube-dl.py info "https://www.youtube.com/watch?v=VIDEO_ID"
```

Returns: title, uploader, duration, views, best available quality, codec info

### List Available Formats

```python
exec: python3 skills/youtube-dl/scripts/youtube-dl.py formats "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Supported URLs

- Single videos: `https://www.youtube.com/watch?v=VIDEO_ID`
- Short URLs: `https://youtu.be/VIDEO_ID`
- Playlists: `https://www.youtube.com/playlist?list=PLAYLIST_ID`
- YouTube Music: `https://music.youtube.com/watch?v=VIDEO_ID`
- Mobile URLs: `https://m.youtube.com/watch?v=VIDEO_ID`

## Output

- **Videos:** MP4 with best available video codec (H.264/VP9) + AAC audio
- **Audio:** MP3 at highest quality (V0/320kbps)
- **Default location:** `~/Downloads/youtube/`
- **Files named:** `{video title}.{ext}`
- **Subtitles:** English subtitles auto-embedded if available

## Quality Selection

The skill automatically selects:
- **Video:** Best resolution (up to 8K) + best audio, merged to MP4
- **Audio:** Best available audio stream, converted to MP3

Manual quality override:
```python
exec: python3 skills/youtube-dl/scripts/youtube-dl.py download "URL" --quality "bestvideo[height<=1080]+bestaudio/best"
```

## Dependencies

The skill automatically installs:
- **yt-dlp** - YouTube downloader (via pipx or direct binary)
- **ffmpeg** - Required for merging high-quality streams (via Homebrew on macOS)

## Tips

- First run may take longer due to dependency installation
- For playlists, all videos download by default
- Use `--audio` for music/podcasts to save space
- Videos with separate audio/video streams are automatically merged
