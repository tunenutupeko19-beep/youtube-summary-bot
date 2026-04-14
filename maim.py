import os
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime

YOUTUBE_VIDEO_ID = "VIDEO_ID_HERE"

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
CLAUDE_API_KEY = os.environ["CLAUDE_API_KEY"]

def get_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja', 'en'])
    text = " ".join([t["text"] for t in transcript])
    return text

def summarize_with_claude(text):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    prompt = f"以下のYouTube動画の内容を日本語でわかりやすく要約してください:\n\n{text[:100000]}"

    data = {
        "model": "claude-3-5-sonnet-latest",
        "max_tokens": 1000,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    return result["content"][0]["text"]

def send_to_slack(message):
    requests.post(SLACK_WEBHOOK_URL, json={"text": message})

def main():
    transcript = get_transcript(YOUTUBE_VIDEO_ID)
    summary = summarize_with_claude(transcript)
    today = datetime.now().strftime("%Y-%m-%d")
    final_message = f"📺 YouTube要約 ({today})\n\n{summary}"
    send_to_slack(final_message)

if __name__ == "__main__":
    main()
