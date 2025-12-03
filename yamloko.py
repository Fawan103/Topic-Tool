import streamlit as st
import requests
from datetime import datetime, timedelta

# ==========================
# CONFIG
# ==========================
API_KEY = " AIzaSyBEkDgN8rmggrbgRSxGznLwrJKkrccWFi0"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# ==========================
# STREAMLIT UI
# ==========================
st.title("📊 YouTube Viral Topics Tool")

days = st.number_input(
    "Enter Days to Search (1–30):",
    min_value=1,
    max_value=30,
    value=5
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
    "awakening path"
]

# ==========================
# FETCH BUTTON
# ==========================
if st.button("Fetch Data"):
    try:
        start_date = (
            datetime.utcnow() - timedelta(days=int(days))
        ).isoformat("T") + "Z"

        results = []

        for keyword in keywords:
            st.write(f"🔎 Searching: **{keyword}**")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "maxResults": 5,
                "publishedAfter": start_date,
                "key": API_KEY
            }

            search_response = requests.get(
                YOUTUBE_SEARCH_URL,
                params=search_params
            )

            if search_response.status_code != 200:
                st.warning("Search API Error")
                continue

            items = search_response.json().get("items", [])

            if not items:
                st.warning(f"No results for: {keyword}")
                continue

            video_ids = [
                i["id"]["videoId"]
                for i in items
                if i.get("id", {}).get("videoId")
            ]

            channel_ids = [
                i["snippet"]["channelId"]
                for i in items
                if i.get("snippet", {}).get("channelId")
            ]

            if not video_ids or not channel_ids:
                continue

            # ==========================
            # VIDEO STATS REQUEST
            # ==========================
            video_params = {
                "part": "statistics",
                "id": ",".join(video_ids),
                "key": API_KEY
            }

            video_response = requests.get(
                YOUTUBE_VIDEO_URL,
                params=video_params
            )

            if video_response.status_code != 200:
                st.warning("Video Stats Error")
                continue

            video_stats = {
                v["id"]: v
                for v in video_response.json().get("items", [])
            }

            # ==========================
            # CHANNEL STATS REQUEST
            # ==========================
            channel_params = {
                "part": "statistics",
                "id": ",".join(channel_ids),
                "key": API_KEY
            }

            channel_response = requests.get(
                YOUTUBE_CHANNEL_URL,
                params=channel_params
            )

            if channel_response.status_code != 200:
                st.warning("Channel Stats Error")
                continue

            channel_stats = {
                c["id"]: c
                for c in channel_response.json().get("items", [])
            }

            # ==========================
            # BUILD RESULTS
            # ==========================
            for item in items:
                video_i_
