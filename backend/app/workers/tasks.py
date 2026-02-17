import json
import logging
from typing import Optional

from sqlmodel import Session

from app.db.session import engine
from app.models.reel import Reel
from app.models.transcript import ReelTranscript
from app.models.chunk import ReelChunk, chunk_text
from app.services.asr import transcribe_video
from app.services.embeddings import embed_text

logger = logging.getLogger(__name__)


def transcribe_and_index_reel(reel_id: int) -> None:
    """
    Background worker: transcribe a reel and build its searchable index.
    
    STATUS FLOW: uploaded -> processing -> ready (or failed)
    
    This function:
    1. Marks the reel as "processing" immediately
    2. Transcribes the video
    3. Saves the full transcript
    4. Chunks the text
    5. Embeds chunks (using embed_text() - same as RAG uses)
    6. Marks reel as "ready" or "failed" on error
    
    RELIABILITY:
    - Catches all exceptions and marks reel as "failed" (prevents stuck states)
    - Uses minimal logging (print + logging)
    - No external services required (embeddings are deterministic)
    
    Args:
        reel_id: ID of the reel to process
    """
    print(f"[WORKER] Starting transcribe_and_index_reel(reel_id={reel_id})")
    logger.info("Starting transcribe_and_index_reel for reel_id=%s", reel_id)

    reel: Optional[Reel] = None

    with Session(engine) as session:
        try:
            # STEP 1: Load the reel
            reel = session.get(Reel, reel_id)
            if not reel:
                logger.warning("Reel not found: reel_id=%s", reel_id)
                print(f"[WORKER] ERROR: Reel {reel_id} not found")
                return

            # STEP 2: Mark as processing (immediately - before any work)
            # This prevents other requests from seeing "uploaded" status and assuming it's not started
            print(f"[WORKER] Marking reel {reel_id} as processing")
            reel.status = "processing"
            session.add(reel)
            session.commit()
            session.refresh(reel)

            # STEP 3: Transcribe video to text
            print(f"[WORKER] Transcribing reel {reel_id}...")
            full_text = transcribe_video(reel.video_url)
            
            if not full_text or not full_text.strip():
                raise ValueError("Transcription returned empty text")
            
            print(f"[WORKER] Transcription complete: {len(full_text)} chars")

            # STEP 4: Save transcript record
            print(f"[WORKER] Saving transcript for reel {reel_id}")
            transcript = ReelTranscript(reel_id=reel.id, full_text=full_text)
            session.add(transcript)
            session.commit()
            session.refresh(transcript)

            # STEP 5: Chunk the text
            print(f"[WORKER] Chunking transcript for reel {reel_id}")
            chunks = chunk_text(full_text)
            
            if not chunks:
                # Chunking returned empty - this is an error
                raise ValueError("Text chunking returned no chunks")
            
            print(f"[WORKER] Created {len(chunks)} chunks")

            # STEP 6: Embed chunks and save to DB
            # CRITICAL: Use embed_text() - the SAME function RAG uses for queries
            # This ensures indexed chunks match query embeddings
            print(f"[WORKER] Embedding {len(chunks)} chunks for reel {reel_id}")
            for i, chunk in enumerate(chunks):
                vec = embed_text(chunk["text"])
                rc = ReelChunk(
                    reel_id=reel.id,
                    chunk_index=chunk["index"],
                    text=chunk["text"],
                    embedding=vec,
                    model_name="stub",  # Always stub for now; change if switching embedding backends
                )
                session.add(rc)
            
            session.commit()
            print(f"[WORKER] Saved {len(chunks)} embeddings")

            # STEP 7: Mark as ready
            print(f"[WORKER] Marking reel {reel_id} as ready")
            reel.status = "ready"
            session.add(reel)
            session.commit()
            session.refresh(reel)

            print(f"[WORKER] ✅ Successfully processed reel {reel_id}")
            logger.info("Successfully processed reel_id=%s", reel_id)

        except Exception as e:
            # ANY error: mark the reel as failed
            # This prevents stuck states where a reel is forever "processing"
            logger.exception("Error processing reel_id=%s: %s", reel_id, e)
            print(f"[WORKER] ❌ ERROR processing reel {reel_id}: {type(e).__name__}: {e}")
            
            if reel is not None:
                try:
                    reel.status = "failed"
                    session.add(reel)
                    session.commit()
                    print(f"[WORKER] Marked reel {reel_id} as failed")
                except Exception as db_err:
                    logger.exception("Failed to update reel status to failed: %s", db_err)
                    print(f"[WORKER] ⚠️  Could not mark reel as failed: {db_err}")
            
            # Do NOT re-raise - let background task complete without crashing
            # The reel status is now "failed" so the user can see what happened

