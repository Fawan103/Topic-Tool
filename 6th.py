import streamlit as st
import requests
from datetime import datetime, timedelta

# ===================================
# YOUTUBE API CONFIG
# ===================================
API_KEY = "AIzaSyBEkDgN8rmggrbgRSxGznLwrJKkrccWFi0"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# ===================================
# STREAMLIT UI
# ===================================
st.set_page_config(page_title="YouTube Viral Topics Tool", layout="wide")

st.title("📊 YouTube Viral Topics Tool")

days = st.number_input(
    "Enter Days to Search (1–30)",
    min_value=1,
    max_value=30,
    value=5,
    step=1,
)

keywords = [
    "manifestation",
    "law of attraction",
    "spiritual awakening",
    "ancient prayers",
    "inner power",
    "consciousness shift",
    "mindset transformation",
    "self-discovery journey",
    "divine wisdom",
    "awakening truth",
    "spiritual growth",
    "you are divine",
    "power of belief",
    "manifest your reality",
    "subconscious programming",
    "inner alchemy",
    "energy healing",
    "soul journey",
    "higher consciousness",
    "awakening path",
]

# ===================================
# MAIN EXECUTION
# ===================================
if st.button("Fetch Data"):

    try:
        # Determine date range
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"

        results = []

        for keyword in keywords:
            st.write(f"🔍 Searching keyword: **{keyword}**")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }

            # Search videos
            search_response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)

            if search_response.status_code != 200:
                st.warning(f"API Search error for '{keyword}': {search_response.text}")
                continue

            items = search_response.json().get("items", [])

            if not items:
                st.warning(f"No results for {keyword}")
                continue

            video_ids = [
                item["id"]["videoId"]
                for item in items
                if item.get("id", {}).get("videoId")
            ]

            channel_ids = [
                item["snippet"]["channelId"]
                for item in items
                if item.get("snippet", {}).get("channelId")
            ]

            if not video_ids or not channel_ids:
                continue

            # ----------------------------
            # Video Stats
            # ----------------------------
            video_params = {
                "part": "statistics",
                "id": ",".join(video_ids),
                "key": API_KEY,
            }

            video_response = requests.get(YOUTUBE_VIDEO_URL, params=video_params)
            video_data = video_response.json()

            video_stats = {
                v["id"]: v for v in video_data.get("items", [])
            }

            # ----------------------------
            # Channel Stats
            # ----------------------------
            channel_params = {
                "part": "statistics",
                "id": ",".join(channel_ids),
                "key": API_KEY,
            }

            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            channel_stats = {
                c["id"]: c for c in channel_data.get("items", [])
            }

            # ----------------------------
            # Build Final Results
            # ----------------------------
            for item in items:

                video_id = item["id"]["videoId"]
                channel_id = item["snippet"]["channelId"]

                if video_id not in video_stats or channel_id not in channel_stats:
                    continue

                views = int(
                    video_stats[video_id]["statistics"].get("viewCount", 0)
                )

                subs = int(
                    channel_stats[channel_id]["statistics"]
                    .get("subscriberCount", 0)
                )

                # Filter small channels only
                if subs < 3000:
                    results.append({
                        "Keyword": keyword,
