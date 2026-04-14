import os
import requests
import xml.etree.ElementTree as ET
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime

CHANNEL_ID = "UCJinHzrgyp2MKWljyyMFvaw"

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
HF_API_KEY = os.environ["HF_API_KEY"]

def get_latest_video_id(channel_id):
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    response = requests.get(rss_url)
    root = ET.fromstring(response.content)

    namespace = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015"
    }

    entry = root.find("atom:entry", namespace)
    video_id = entry.find("yt:videoId", namespace).text

    return video_id


def get_transcript(video_id):
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id, languages=['ja', 'en'])
    text = " ".join([t.text for t in transcript])
    return text


def summarize_with_hf(text):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": text[:2000]}

    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()

    if isinstance(result, list):
        return result[0]["summary_text"]
    else:
        return "要約に失敗しました"

def send_to_slack(message):
    requests.post(SLACK_WEBHOOK_URL, json={"text": message})

def main():
    video_id = get_latest_video_id(CHANNEL_ID)
    transcript = get_transcript(video_id)
    summary = summarize_with_hf(transcript)
    today = datetime.now().strftime("%Y-%m-%d")
    final_message = f"📺 最新動画要約 ({today})\n\n{summary}"
    send_to_slack(final_message)

if __name__ == "__main__":
    main()
