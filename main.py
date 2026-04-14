import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

CHANNEL_ID = "UCJinHzrgyp2MKWljyyMFvaw"

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
HF_API_KEY = os.environ["HF_API_KEY"]

def get_latest_video_info(channel_id):
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    response = requests.get(rss_url)
    root = ET.fromstring(response.content)

    namespace = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015"
    }

    entry = root.find("atom:entry", namespace)

    title = entry.find("atom:title", namespace).text
    video_id = entry.find("yt:videoId", namespace).text
    link = entry.find("atom:link", namespace).attrib["href"]
    description = entry.find("atom:content", namespace).text

    return title, description, link

def analyze_with_hf(title, description):
    API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    prompt = f"""
以下のYouTube動画について分析してください。

タイトル:
{title}

概要:
{description}

出力形式:
1. 3行要約
2. 見る価値（高・中・低）
3. 重要ポイント3つ
4. どんな人向けか
"""

    payload = {"inputs": prompt[:2000]}

    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()

    if isinstance(result, list):
        return result[0]["generated_text"]
    else:
        return "分析に失敗しました"

def send_to_slack(message):
    requests.post(SLACK_WEBHOOK_URL, json={"text": message})

def main():
    title, description, link = get_latest_video_info(CHANNEL_ID)
    analysis = analyze_with_hf(title, description)

    today = datetime.now().strftime("%Y-%m-%d")

    final_message = f"""
📺 新着動画チェック ({today})

🎬 タイトル:
{title}

🔗 URL:
{link}

{analysis}
"""

    send_to_slack(final_message)

if __name__ == "__main__":
    main()
