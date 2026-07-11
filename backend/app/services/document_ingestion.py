"""Timestamp-aware transcript ingestion."""

from __future__ import annotations

import re
from dataclasses import dataclass

from youtube_transcript_api import TranscriptsDisabled, YouTubeTranscriptApi
from youtube_transcript_api._transcripts import TranscriptList

_MULTI_SPACE = re.compile(r"\s+")


@dataclass
class TranscriptSegment:
    """A transcript snippet with its position in the video."""

    text: str
    start: float
    duration: float


def _clean(text: str) -> str:
    """Collapse whitespace and strip."""
    return _MULTI_SPACE.sub(" ", text).strip()


def _select_transcript(transcript_list: TranscriptList):
    """Language preference cascade."""
    try:
        return transcript_list.find_manually_created_transcript(
            ["en", "en-US", "en-GB"]
        )
    except Exception:
        pass
    try:
        return transcript_list.find_generated_transcript(["en", "en-US", "en-GB"])
    except Exception:
        pass
    try:
        return next(t for t in transcript_list if not t.is_generated)
    except StopIteration:
        pass
    try:
        return next(iter(transcript_list))
    except StopIteration as exc:
        raise ValueError("No transcripts are available for this video.") from exc


def fetch_transcript_segments(video_id: str) -> list[TranscriptSegment]:
    """Return timestamped transcript segments."""
    try:
        transcript_list: TranscriptList = YouTubeTranscriptApi().list(video_id)
    except TranscriptsDisabled as exc:
        raise ValueError("Captions are disabled for this video.") from exc
    except Exception as exc:
        raise ValueError(f"Could not list transcripts: {exc}") from exc

    transcript = _select_transcript(transcript_list)

    try:
        snippets = transcript.fetch()
    except Exception as exc:
        raise ValueError(f"Could not fetch transcript: {exc}") from exc

    segments: list[TranscriptSegment] = []
    for snip in snippets:
        text = getattr(snip, "text", None)
        start = getattr(snip, "start", None)
        duration = getattr(snip, "duration", None)
        if text is None and isinstance(snip, dict):
            text = snip.get("text", "")
            start = snip.get("start", 0.0)
            duration = snip.get("duration", 0.0)

        cleaned = _clean(text or "")
        if not cleaned:
            continue
        segments.append(
            TranscriptSegment(
                text=cleaned,
                start=float(start or 0.0),
                duration=float(duration or 0.0),
            )
        )

    if not segments:
        raise ValueError("The video transcript is empty.")
    return segments


def fetch_transcript(video_id: str) -> str:
    """Backwards-compatible: whole transcript as one string."""
    segments = fetch_transcript_segments(video_id)
    return _clean(" ".join(seg.text for seg in segments))