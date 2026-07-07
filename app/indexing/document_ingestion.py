from youtube_transcript_api import TranscriptsDisabled, YouTubeTranscriptApi

video_id="Gfr50f6ZBvo"
ytt_api = YouTubeTranscriptApi()
try:
    transcript_list = ytt_api.fetch(video_id,languages=['en'])

    #flatten it to plain text

    transcript=" ".join(chunk.text for chunk in transcript_list)
    print(transcript) 
except TranscriptsDisabled:
   print("No captions available for this video")


   