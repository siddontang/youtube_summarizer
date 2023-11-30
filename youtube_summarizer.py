import re
import sys
import os
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # Load environment variables from .env file


def get_video_id(youtube_url):
    """
    Extract the video ID from the YouTube URL.
    """
    match = re.search(r"(?<=v=)[^&#]+", youtube_url)
    match = match or re.search(r"(?<=be/)[^&#]+", youtube_url)
    video_id = match.group(0) if match else None
    return video_id


def get_transcript(video_id):
    """
    Fetch the default transcript for the given video ID.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([item['text'] for item in transcript])
    except Exception as e:
        print("Error fetching transcript:", e)
        return None


def summarize_transcript(transcript):
    """
    Use OpenAI API to summarize the transcript with GPT-4 engine.
    """

    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
    )

    prompt_text = (
        "Please provide a concise summary and key points of the following transcript in Markdown format:\n\n"
        "### Summary:\n\n"
        "### Key Points:\n\n"
    )

    completion = client.chat.completions.create(
        model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
        messages=[
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": "Summarize the following text:\n\n" + transcript}
        ],
    )

    return completion.choices[0].message.content


def youtube_summazier(youtube_url):
    """
    Summarize the transcript of a YouTube video and output in Markdown format.
    """
    video_id = get_video_id(youtube_url)
    if not video_id:
        return "Invalid YouTube URL."

    transcript = get_transcript(video_id)
    if not transcript:
        return "Transcript not available."

    summary = summarize_transcript(transcript)
    return f"## Summary\n\n{summary}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python youtube_summazier.py [YouTube URL]")
    else:
        youtube_url = sys.argv[1]
        summary_markdown = youtube_summazier(youtube_url)
        print(summary_markdown)
