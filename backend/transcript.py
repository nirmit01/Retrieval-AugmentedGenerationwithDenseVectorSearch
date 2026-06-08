# transcript.py
# Handles YouTube URL parsing and transcript fetching

from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled


def get_video_id(url: str) -> str | None:
    """Extract the video ID from any valid YouTube URL format."""
    parsed = urlparse(url)

    # Handle youtu.be short links
    if parsed.hostname in ("youtu.be", "www.youtu.be"):
        return parsed.path.lstrip("/")

    # Handle standard youtube.com URLs
    if parsed.hostname in ("youtube.com", "www.youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            qs = parse_qs(parsed.query)
            return qs.get("v", [None])[0]
        for prefix in ("/embed/", "/v/"):
            if parsed.path.startswith(prefix):
                return parsed.path.split(prefix)[-1]

    return None


def fetch_transcript(video_id: str) -> str:
    """
    Fetch the transcript for a given YouTube video ID.
    Uses the v1.x API that matches the Colab notebook logic.
    """
    ytt_api = YouTubeTranscriptApi()

    try:
        # Fetch the default (English) transcript
        fetched_transcript = ytt_api.fetch(video_id)
        # Convert to a list of raw dicts
        raw_transcript = fetched_transcript.to_raw_data()
        # Join all text snippets into one continuous string
        transcript = " ".join(item["text"] for item in raw_transcript)
        return transcript

    except TranscriptsDisabled:
        raise ValueError("No captions/transcript available for this video.")
    except Exception as e:
        raise ValueError(f"Could not fetch transcript: {str(e)}")


def get_transcript_from_url(url: str) -> tuple[str, str]:
    """
    Full pipeline: URL → video_id → transcript text.
    Returns (video_id, transcript_text).
    """
    print(f"Processing URL: {url}")
    video_id = get_video_id(url)
    print(f"Extracted video ID: {video_id}")

    if not video_id:
        raise ValueError("Invalid YouTube URL. Could not extract video ID.")

    transcript = fetch_transcript(video_id)
    return video_id, transcript
