import os
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime

YOUTUBE_VIDEO_ID = "VIDEO_ID_HERE"

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
HF_API_KEY = os.environ["HF_API_KEY"]

def get_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja', 'en'])
    text = " ".join([t["text"] for t in transcript])
    return text

def summarize_with_hf(text):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    payload = {
        "inputs": text[:2000]
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()

    if isinstance(result, list):
        return result[0]["summary_text"]
    else:
        return "要約に失敗しました"

def send_to_slack(message):
    requests.post(SLACK_WEBHOOK_URL, json={"text": message})

def main():
    transcript = get_transcript(YOUTUBE_VIDEO_ID)
    summary = summarize_with_hf(transcript)
    today = datetime.now().strftime("%Y-%m-%d")
    final_message = f"📺 YouTube要約 ({today})\n\n{summary}"
    send_to_slack(final_message)

if __name__ == "__main__":
    main()
