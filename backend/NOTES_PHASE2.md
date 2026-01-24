# Phase 2 – Transcription + Indexing (Reel RAG backend)

Goal: When a reel is uploaded, a background job should:
1. Mark the reel as `status="processing"`.
2. Transcribe the video file into text.
3. Save the full transcript in `ReelTranscript`.
4. Chunk the transcript into overlapping chunks.
5. Embed each chunk into a vector.
6. Save each chunk + embedding in `ReelChunk`.
7. Mark the reel as `status="ready"` or `"failed"` on error.

Constraints:
- I am a student; keep it FREE by default.
- ASR and embeddings should have **stub modes** controlled by env vars:
  - `ASR_MODE=stub` (default) → return fake transcript.
  - `EMBED_MODE=stub` (default) → return cheap fake vector.
- Real OpenAI/Whisper support can be added later behind `ASR_MODE=openai` and `EMBED_MODE=openai`, but for now they can raise `NotImplementedError`.
