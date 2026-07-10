from youtube_transcript_api import TranscriptsDisabled, YouTubeTranscriptApi
from youtube_transcript_api._transcripts import TranscriptList


def fetch_transcript(video_id: str) -> str:
    """Fetch transcript in any available language, preferring English."""
    try:
        transcript_list: TranscriptList = YouTubeTranscriptApi().list(video_id)
    except TranscriptsDisabled as exc:
        raise ValueError("Captions are disabled for this video.") from exc
    except Exception as exc:
        raise ValueError(f"Could not list transcripts for this video: {exc}") from exc

    # Priority order: manual English → auto English → any manual → any auto
    try:
        transcript = transcript_list.find_manually_created_transcript(["en", "en-US", "en-GB"])
    except Exception:
        try:
            transcript = transcript_list.find_generated_transcript(["en", "en-US", "en-GB"])
        except Exception:
            try:
                # Fall back to first available manually created transcript in any language
                transcript = next(
                    t for t in transcript_list if not t.is_generated
                )
            except StopIteration:
                try:
                    # Last resort: first auto-generated transcript in any language
                    transcript = next(iter(transcript_list))
                except StopIteration:
                    raise ValueError("No transcripts are available for this video.")

    try:
        snippets = transcript.fetch()
    except Exception as exc:
        raise ValueError(f"Could not fetch the transcript: {exc}") from exc

    text = " ".join(snippet.text for snippet in snippets).strip()
    if not text:
        raise ValueError("The video transcript is empty.")
    return text