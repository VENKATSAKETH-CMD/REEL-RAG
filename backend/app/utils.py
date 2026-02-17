"""
Utility functions for the Reel RAG backend.
"""

from pathlib import Path


def get_public_video_url(video_path: str, base_url: str = "http://localhost:8000") -> str:
    """
    Convert a local filesystem video path to a publicly accessible HTTP URL.
    
    Example:
        get_public_video_url("./data/uploads/abc123.mp4")
        → "http://localhost:8000/uploads/abc123.mp4"
    
    Args:
        video_path: Local filesystem path (relative or absolute)
        base_url: Base URL for the API server (default: http://localhost:8000)
    
    Returns:
        Full HTTP URL that the browser can load
    """
    # Convert to Path object for consistent handling
    path = Path(video_path)
    
    # Extract just the filename (last component)
    filename = path.name
    
    # Return the public HTTP URL
    return f"{base_url}/uploads/{filename}"
