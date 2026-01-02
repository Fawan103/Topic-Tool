import streamlit as st
import requests
from datetime import datetime, timedelta
import re

# ===================================
# YOUTUBE API CONFIG
# ===================================
API_KEY = "AIzaSyBEkDgN8rmggrbgRSxGznLwrJKkrccWFi0"

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# ===================================
# STREAMLIT UI
# ===================================
st.set_page_config(page_title="Rare Car Stories Viral Tool", layout="wide")
st.title("🚗 Rare Car Stories & Automotive History Viral Topics Tool")

days = st.number_input("Enter Days to Search (1–30)", 1, 30, 5)

# ===================================
# AUTOMOTIVE HISTORY / RARE CARS KEYWORDS (NEW LIST ONLY)
# ===================================
keywords = [
    "rare car stories",
    "automotive history rare cars",
    "vintage muscle cars history",
    "banned engines stories",
    "classic car raconteurs",
    "rare engine legends",
    "427 Ford story",
    "351 Cleveland cammed history",
    "Ford Boss 429 legacy",
    "hidden Corvette legends",
    "Indy engine innovations",
    "Smokey Yunick twin-turbo Chevy 207 story",
    "banned big block history",
    "drag racing legends history",
    "forgotten prototypes cars",
    "NASCAR historical scandals",
    "rare car barn finds",
    "vintage race car tales",
    "classic Buick rare builds",
    "Pontiac Super Duty history",
    "unique Mopar stories",
    "muscle car underdog victories",
    "automotive engineering breakthroughs",
    "rare Ford GT40 backstory",
    "historical car controversy",
    "rare prototypes never released",
    "classic car heritage deep dive",
    "automotive innovation pioneers",
    "legendary race car engineers",
    "obscure vintage car discoveries",
    "classic racing dynasties",
    "Ford vs Chevy legendary battles",
    "historic drag car build stories",
    "rare automotive banishment tales",
    "one-off automotive legends"
]

# ===================================
# HELPER — ISO DURATION TO MINUTES
# ===================================
def iso_to_minutes(iso):
    if not iso:
        return 0.0
    h = m = s = 0
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if match:
        h = int(match.group(1) or 0)
        m = int(match.group(2) or 0)
        s = int(match.group(3) or 0)
    return round((h * 3600 + m * 60 + s) / 60, 1)

# ===================================
# MAIN
# ===================================
if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        results = []

        for keyword in keywords:
            st.write(f"🔍 Searching: {keyword}")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "relevanceLanguage": "en",
                "key": API_KEY,
            }

            search_resp = requests.get(SEARCH_URL, params=search_params)
            if search_resp.status_code != 200:
                continue

            items = search_resp.json().get("items", [])
            if not items:
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

            # ----- VIDEO DATA -----
