from youtube_transcript_api import TranscriptsDisabled, YouTubeTranscriptApi


def fetch_transcript(video_id: str) -> str:
    """Fetch an English YouTube transcript and flatten it to plain text."""
    try:
        snippets = YouTubeTranscriptApi().fetch(video_id, languages=["en"])
    except TranscriptsDisabled as exc:
        raise ValueError("Captions are disabled for this video.") from exc
    except Exception as exc:
        raise ValueError(f"Could not fetch the video transcript: {exc}") from exc

    transcript = " ".join(snippet.text for snippet in snippets).strip()
    if not transcript:
        raise ValueError("The video transcript is empty.")
    return transcript