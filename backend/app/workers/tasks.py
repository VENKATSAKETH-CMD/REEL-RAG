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
    Synchronous worker:
    - Load reel
    - Mark processing
    - Transcribe video -> full_text
    - Save ReelTranscript
    - Chunk + embed -> ReelChunk rows
    - Mark ready / failed
    """
    print(f"[WORKER] Starting transcribe_and_index_reel({reel_id})")
    logger.info("Starting transcribe_and_index_reel for reel_id=%s", reel_id)

    reel: Optional[Reel] = None

    with Session(engine) as session:
        try:
            # 1. Load reel
            reel = session.get(Reel, reel_id)
            if not reel:
                logger.warning("Reel %s not found", reel_id)
                print(f"[WORKER] Reel {reel_id} not found")
                return

            # 2. status -> processing
            print("[WORKER] Status -> processing")
            reel.status = "processing"
            session.add(reel)
            session.commit()
            session.refresh(reel)

            # 3. Transcribe
            full_text = transcribe_video(reel.video_url)

            # 4. Save transcript
            transcript = ReelTranscript(reel_id=reel.id, full_text=full_text)
            session.add(transcript)
            session.commit()
            session.refresh(transcript)

            # 5. Chunk text
            chunks = chunk_text(full_text)

            # 6. Embed + save chunks
            for chunk in chunks:
                vec = embed_text(chunk["text"])
                rc = ReelChunk(
                    reel_id=reel.id,
                    chunk_index=chunk["index"],
                    text=chunk["text"],
                    embedding=vec,
                    model_name="stub",
                )
                # If the model has a pgvector column, store the vector there too.
                # Check table columns to ensure the column exists in the current DB schema.
                # Always set embedding vector; RAG assumes Postgres+pgvector
                rc.embedding = vec
                session.add(rc)

            session.commit()

            # 7. status -> ready
            print("[WORKER] Status -> ready")
            reel.status = "ready"
            session.add(reel)
            session.commit()
            session.refresh(reel)

            print(f"[WORKER] Finished transcribe_and_index_reel({reel_id}) successfully")
            logger.info(
                "Finished transcribe_and_index_reel OK for reel_id=%s", reel_id
            )

        except Exception:
            logger.exception(
                "Error in transcribe_and_index_reel for reel_id=%s", reel_id
            )
            if reel is not None:
                # mark failed
                reel.status = "failed"
                session.add(reel)
                session.commit()
            # re-raise in case we want to see it during dev
            raise
