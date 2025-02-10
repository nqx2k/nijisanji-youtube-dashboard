import os
import requests
import json
import time

# GitHub Secrets から APIキーを取得
API_KEYS = [
    os.getenv("YOUTUBE_API_KEY_1"),
    os.getenv("YOUTUBE_API_KEY_2"),
    os.getenv("YOUTUBE_API_KEY_3")
]
api_index = 0

# チャンネルIDリストを取得
with open("channels.json", "r", encoding="utf-8") as file:
    channels = json.load(file)

# APIキーを順番にローテーション
def get_api_key():
    global api_index
    key = API_KEYS[api_index]
    api_index = (api_index + 1) % len(API_KEYS)
    return key

# YouTube API から動画を取得
def fetch_videos(channel_id, channel_name):
    api_key = get_api_key()
    url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&type=video&order=date&maxResults=5"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return []

    data = response.json()
    videos = []
    for item in data.get("items", []):
        if "videoId" in item["id"]:
            videos.append({
                "title": item["snippet"]["title"],
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                "videoId": item["id"]["videoId"],
                "channelName": channel_name,  # チャンネル名を追加
                "publishedAt": item["snippet"]["publishedAt"]  # 投稿日時を追加
            })
    
    return videos

# 最新動画を取得し、キャッシュに保存
def update_cached_videos():
    cached_videos = []
    
    for channel in channels:
        channel_id = channel["id"]
        channel_name = channel["name"]
        print(f"Fetching videos for {channel_id} ({channel_name})...")
        videos = fetch_videos(channel_id, channel_name)
        cached_videos.extend(videos)
        time.sleep(1)
    
    # JSONファイルに保存
    with open("cached_videos.json", "w", encoding="utf-8") as file:
        json.dump(cached_videos, file, ensure_ascii=False, indent=4)

    print("✅ 最新動画情報をキャッシュしました！")

# 実行
if __name__ == "__main__":
    update_cached_videos()
