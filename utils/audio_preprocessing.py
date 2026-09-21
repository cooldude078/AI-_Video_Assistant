import os
import shutil

import yt_dlp
from pydub import AudioSegment

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _ensure_ffmpeg_on_path() -> str:
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    candidate_dirs = [
        r"C:\Program Files\FFmpeg\bin",
        r"C:\Program Files (x86)\FFmpeg\bin",
        r"C:\ffmpeg\bin",
        r"C:\Users\anish\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin",
    ]

    for directory in candidate_dirs:
        if os.path.isdir(directory):
            ffmpeg_path = os.path.join(directory, "ffmpeg.exe")
            if os.path.exists(ffmpeg_path):
                os.environ["PATH"] = directory + os.pathsep + os.environ.get("PATH", "")
                return ffmpeg_path

    raise RuntimeError(
        "FFmpeg is not installed or not available on PATH. "
        "Install FFmpeg and restart your terminal before downloading audio."
    )


def download_youtube_audio(url: str) -> str:
    if not url:
        raise ValueError("A YouTube URL is required.")

    _ensure_ffmpeg_on_path()

    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if not info:
            raise ValueError("No metadata was returned for the given URL.")

        filename = ydl.prepare_filename(info)
        filename = filename.replace(".webm", ".wav").replace(".m4a", ".wav")

    return filename


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz
    audio.export(output_path, format="wav")
    return output_path

def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 

    chunks = []

    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format = "wav")

        chunks.append(chunk_path)
    
    return chunks

def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks



    



