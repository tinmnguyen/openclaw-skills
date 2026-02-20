#!/usr/bin/env python3
"""
YouTube Video Downloader using yt-dlp
Auto-installs yt-dlp and ffmpeg if not present.
"""

import os
import sys
import json
import subprocess
import re
import platform
from urllib.parse import urlparse

YTDLP_PATH = os.path.expanduser("~/.local/bin/yt-dlp")
FFMPEG_PATH = os.path.expanduser("~/.local/bin/ffmpeg")

def run_cmd(cmd, timeout=60, capture=True):
    """Run a command with optional timeout."""
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result
        else:
            result = subprocess.run(cmd, timeout=timeout)
            return result
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        return type('obj', (object,), {'returncode': -1, 'stderr': str(e), 'stdout': ''})()

def ensure_ffmpeg():
    """Ensure ffmpeg is installed, installing if necessary."""
    # Check if ffmpeg is in PATH
    result = run_cmd(['ffmpeg', '-version'], timeout=5)
    if result and result.returncode == 0:
        return 'ffmpeg'
    
    # Check if installed in ~/.local/bin
    if os.path.exists(FFMPEG_PATH):
        return FFMPEG_PATH
    
    # Try to install via Homebrew on macOS
    system = platform.system()
    if system == 'Darwin':
        print("Installing ffmpeg via Homebrew...", file=sys.stderr)
        result = run_cmd(['brew', 'install', 'ffmpeg'], timeout=300)
        if result and result.returncode == 0:
            # Verify it's now available
            result = run_cmd(['ffmpeg', '-version'], timeout=5)
            if result and result.returncode == 0:
                return 'ffmpeg'
    
    # Try static binary installation
    print("Installing ffmpeg static binary...", file=sys.stderr)
    os.makedirs(os.path.dirname(FFMPEG_PATH), exist_ok=True)
    
    try:
        if system == 'Darwin':
            # macOS - use brew if possible, otherwise warn
            print("Please install ffmpeg manually: brew install ffmpeg", file=sys.stderr)
            return None
        else:
            # Linux - download static binary
            arch = platform.machine()
            if arch == 'x86_64':
                url = 'https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz'
            elif arch == 'aarch64':
                url = 'https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linuxarm64-gpl.tar.xz'
            else:
                print(f"Unsupported architecture: {arch}. Please install ffmpeg manually.", file=sys.stderr)
                return None
            
            # Download and extract
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                tar_path = os.path.join(tmpdir, 'ffmpeg.tar.xz')
                subprocess.run(['curl', '-L', '-o', tar_path, url], check=True, timeout=120)
                subprocess.run(['tar', '-xf', tar_path, '-C', tmpdir], check=True)
                
                # Find ffmpeg binary
                for root, dirs, files in os.walk(tmpdir):
                    if 'ffmpeg' in files:
                        src = os.path.join(root, 'ffmpeg')
                        import shutil
                        shutil.copy2(src, FFMPEG_PATH)
                        os.chmod(FFMPEG_PATH, 0o755)
                        break
            
            # Verify
            result = run_cmd([FFMPEG_PATH, '-version'], timeout=5)
            if result and result.returncode == 0:
                print(f"ffmpeg installed to {FFMPEG_PATH}", file=sys.stderr)
                return FFMPEG_PATH
    except Exception as e:
        print(f"Failed to install ffmpeg: {e}", file=sys.stderr)
    
    return None

def ensure_ytdlp():
    """Ensure yt-dlp is installed, installing if necessary."""
    # Check if yt-dlp is in PATH
    result = run_cmd(['yt-dlp', '--version'], timeout=5)
    if result and result.returncode == 0:
        return 'yt-dlp'
    
    # Check if installed in ~/.local/bin
    if os.path.exists(YTDLP_PATH):
        return YTDLP_PATH
    
    # Install yt-dlp
    print("Installing yt-dlp...", file=sys.stderr)
    os.makedirs(os.path.dirname(YTDLP_PATH), exist_ok=True)
    
    try:
        # Try pipx first if available
        pipx_result = run_cmd(['pipx', 'install', 'yt-dlp'], timeout=60)
        if pipx_result and pipx_result.returncode == 0:
            result = run_cmd(['yt-dlp', '--version'], timeout=5)
            if result and result.returncode == 0:
                return 'yt-dlp'
    except:
        pass
    
    try:
        # Download yt-dlp binary directly
        subprocess.run([
            'curl', '-L', '-o', YTDLP_PATH,
            'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp'
        ], check=True, timeout=120)
        
        os.chmod(YTDLP_PATH, 0o755)
        
        # Verify
        result = run_cmd([YTDLP_PATH, '--version'], timeout=5)
        if result and result.returncode == 0:
            print(f"yt-dlp installed to {YTDLP_PATH}", file=sys.stderr)
            return YTDLP_PATH
    except Exception as e:
        print(f"Failed to install yt-dlp: {e}", file=sys.stderr)
        print("Please install manually: pip install yt-dlp", file=sys.stderr)
        sys.exit(1)

def is_valid_youtube_url(url):
    """Check if URL is a valid YouTube URL."""
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return False
    
    youtube_domains = ['youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com', 'music.youtube.com']
    return any(domain in parsed.netloc for domain in youtube_domains)

def get_video_info(url, ytdlp_cmd):
    """Get video info without downloading."""
    try:
        result = run_cmd([ytdlp_cmd, '--dump-json', '--no-download', url], timeout=30)
        if result and result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if lines:
                return json.loads(lines[0])
        return None
    except Exception as e:
        print(f"Error getting video info: {e}", file=sys.stderr)
        return None

def download_video(url, ytdlp_cmd, ffmpeg_cmd, output_dir=None, audio_only=False, quality=None):
    """Download video or audio from YouTube with highest quality."""
    
    if not is_valid_youtube_url(url):
        return {"success": False, "error": "Invalid YouTube URL"}
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.expanduser("~/Downloads/youtube")
    os.makedirs(output_dir, exist_ok=True)
    
    # Build yt-dlp command
    cmd = [ytdlp_cmd]
    
    if audio_only:
        # Audio only - best quality audio
        cmd.extend([
            '-f', 'bestaudio/best',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', quality or '0',
        ])
        output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
    else:
        # Video - highest quality format selection
        # This format string tries best quality mp4 first, then any best quality
        format_spec = quality or 'bestvideo*+bestaudio/best'
        cmd.extend(['-f', format_spec])
        
        # Add merge output format for when video/audio are separate
        cmd.extend(['--merge-output-format', 'mp4'])
        
        output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
    
    cmd.extend(['-o', output_template])
    
    # Add ffmpeg location if not in PATH
    if ffmpeg_cmd and ffmpeg_cmd != 'ffmpeg':
        cmd.extend(['--ffmpeg-location', os.path.dirname(ffmpeg_cmd)])
    
    # Add progress and metadata options
    cmd.extend([
        '--newline',
        '--no-warnings',
        '--embed-metadata',
        '--embed-thumbnail' if audio_only else '--write-thumbnail',
        '--embed-subs',  # Embed subtitles if available
        '--sub-langs', 'en',  # Download English subtitles
    ])
    
    # Add URL
    cmd.append(url)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for large files
        )
        
        if result.returncode == 0:
            # Extract output filename
            output_files = []
            for line in result.stdout.split('\n'):
                if '[download] Destination:' in line:
                    filepath = line.split('Destination:')[1].strip()
                    output_files.append(filepath)
                elif '[Merger]' in line and 'Merging formats into' in line:
                    match = re.search(r'\"(.+?)\"', line)
                    if match:
                        output_files.append(match.group(1))
                elif '[ExtractAudio]' in line and 'Destination:' in line:
                    match = re.search(r'Destination:\s*(.+)', line)
                    if match:
                        output_files.append(match.group(1).strip())
            
            # Also check for files in output directory
            if not output_files:
                for f in os.listdir(output_dir):
                    if not f.endswith(('.part', '.ytdl', '.webp')):
                        full_path = os.path.join(output_dir, f)
                        if os.path.getmtime(full_path) > time.time() - 60:  # Modified in last minute
                            output_files.append(full_path)
            
            return {
                "success": True,
                "output_files": output_files,
                "output_dir": output_dir
            }
        else:
            return {
                "success": False,
                "error": result.stderr or "Unknown error",
                "stdout": result.stdout
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Download timed out (10 minutes)"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_formats(url, ytdlp_cmd):
    """List available formats for a video."""
    try:
        result = run_cmd([ytdlp_cmd, '--list-formats', url], timeout=30)
        if result and result.returncode == 0:
            return {"success": True, "formats": result.stdout}
        else:
            return {"success": False, "error": result.stderr if result else "Failed to list formats"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    import time  # Import here for file timestamp checking
    
    # Ensure yt-dlp is available
    ytdlp_cmd = ensure_ytdlp()
    
    # Ensure ffmpeg is available (for merging high quality streams)
    ffmpeg_cmd = ensure_ffmpeg()
    if not ffmpeg_cmd:
        print("Warning: ffmpeg not available. Some high-quality downloads may fail.", file=sys.stderr)
    
    if len(sys.argv) < 2:
        print("Usage: youtube-dl.py <command> [options]", file=sys.stderr)
        print("Commands: download, info, formats", file=sys.stderr)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "info":
        if len(sys.argv) < 3:
            print("Usage: youtube-dl.py info <url>", file=sys.stderr)
            sys.exit(1)
        url = sys.argv[2]
        info = get_video_info(url, ytdlp_cmd)
        if info:
            # Show available quality info
            formats = info.get("formats", [])
            video_formats = [f for f in formats if f.get("vcodec") != "none"]
            audio_formats = [f for f in formats if f.get("acodec") != "none"]
            
            # Get best video quality
            best_video = None
            for f in sorted(video_formats, key=lambda x: x.get("height", 0), reverse=True):
                if f.get("height"):
                    best_video = f
                    break
            
            simplified = {
                "title": info.get("title"),
                "uploader": info.get("uploader"),
                "duration": info.get("duration_string"),
                "views": info.get("view_count"),
                "upload_date": info.get("upload_date"),
                "description": info.get("description", "")[:500] if info.get("description") else None,
                "thumbnail": info.get("thumbnail"),
                "best_video_quality": f"{best_video.get('height', 'unknown')}p" if best_video else "unknown",
                "best_video_codec": best_video.get("vcodec", "unknown") if best_video else "unknown",
            }
            print(json.dumps(simplified, indent=2, default=str))
        else:
            print(json.dumps({"error": "Could not fetch video info"}))
    
    elif command == "download":
        if len(sys.argv) < 3:
            print("Usage: youtube-dl.py download <url> [--audio] [--quality <quality>] [--output <dir>]", file=sys.stderr)
            sys.exit(1)
        
        url = sys.argv[2]
        audio_only = '--audio' in sys.argv
        quality = None
        output_dir = None
        
        # Parse optional args
        for i, arg in enumerate(sys.argv):
            if arg == '--quality' and i + 1 < len(sys.argv):
                quality = sys.argv[i + 1]
            elif arg == '--output' and i + 1 < len(sys.argv):
                output_dir = sys.argv[i + 1]
        
        result = download_video(url, ytdlp_cmd, ffmpeg_cmd, output_dir, audio_only, quality)
        print(json.dumps(result, indent=2, default=str))
    
    elif command == "formats":
        if len(sys.argv) < 3:
            print("Usage: youtube-dl.py formats <url>", file=sys.stderr)
            sys.exit(1)
        url = sys.argv[2]
        result = list_formats(url, ytdlp_cmd)
        print(json.dumps(result, indent=2, default=str))
    
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print("Commands: download, info, formats", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
