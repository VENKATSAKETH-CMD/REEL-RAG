"""
Phase 2 — ASR (Transcription) Service

Handles automatic speech recognition for video transcription.
Supports multiple backends (stub, OpenAI Whisper, etc.)
"""


import os
import tempfile
import subprocess
import time
from typing import Optional

try:
    import openai
except ImportError:
    openai = None


def transcribe_video(path: str) -> str:
    """
    Transcribe audio/video file to text.

    Args:
        path: File path to the audio/video file

    Returns:
        Transcribed text

    Raises:
        NotImplementedError: If backend is not yet implemented
        ValueError: If ASR_MODE is invalid
    """
    asr_mode = os.getenv("ASR_MODE", "stub").lower()

    if asr_mode == "stub":
        # Return deterministic fake transcript
        return f"[STUB TRANSCRIPT] This is a fake transcript for {path}"

    elif asr_mode == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set. Cannot use OpenAI Whisper ASR.")
        if openai is None:
            raise RuntimeError("openai package is not installed.")

        # Extract audio to a temporary file (wav, 16kHz mono)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp_audio:
            audio_path = tmp_audio.name
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-i", path,
                "-ar", "16000", "-ac", "1", "-f", "wav", audio_path
            ]
            ffmpeg_proc = subprocess.run(ffmpeg_cmd, capture_output=True)
            if ffmpeg_proc.returncode != 0:
                raise RuntimeError(f"ffmpeg failed to extract audio: {ffmpeg_proc.stderr.decode(errors='ignore')}")

            # Call OpenAI Whisper API
            model = os.getenv("OPENAI_WHISPER_MODEL", "whisper-1")
            openai.api_key = api_key
            start = time.time()
            with open(audio_path, "rb") as audio_file:
                try:
                    transcript = openai.audio.transcriptions.create(
                        model=model,
                        file=audio_file
                    )
                except Exception as e:
                    raise RuntimeError(f"OpenAI Whisper API error: {e}")
            duration = time.time() - start
            print(f"[ASR] Transcription completed in {duration:.2f}s for {path}")
            # transcript.text is the full transcript
            return transcript.text

    else:
        raise ValueError(f"Invalid ASR_MODE: {asr_mode}. Must be 'stub' or 'openai'")
