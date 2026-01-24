"""
Phase 2 — ASR (Transcription) Service

Handles automatic speech recognition for video transcription.
Supports multiple backends (stub, OpenAI Whisper, etc.)
"""

import os


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
        raise NotImplementedError("OpenAI Whisper not wired yet")

    else:
        raise ValueError(f"Invalid ASR_MODE: {asr_mode}. Must be 'stub' or 'openai'")
