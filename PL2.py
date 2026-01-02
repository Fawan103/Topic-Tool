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
# AUTOMOTIVE HISTORY KEYWORDS
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
        return 0
    h = m = s = 0
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if match:
        h = int(match.group(1)) if match.group(1) else 0
        m = int(match.group(2)) if match.group(2) else 0
        s = int(match.group(3)) if match.group(3) else 0
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
                "key": API_KEY
            }

            search_resp = requests.get(SEARCH_URL, params=search_params)
            if search_resp.status_code != 200:
                continue

            items = search_resp.json().get("items", [])
            if not items:
                continue

            video_ids = [
                i.get("id", {}).get("videoId")
                for i in items
                if i.get("id", {}).get("videoId")
            ]

            channel_ids = [
                i.get("snippet", {}).get("channelId")
                for i in items
                if i.get("snippet", {}).get("channelId")
            ]

            if not video_ids:
                continue

            # ----- VIDEO DATA -----
            v_resp = requests.get(
                VIDEO_URL,
                params={
                    "part": "statistics,contentDetails",
                    "id": ",".join(video_ids),
                    "key": API_KEY
                }
            )

            if v_resp.status_code != 200:
                continue

            video_lookup = {v["id"]: v for v in v_resp.json().get("items", [])}

            # ----- CHANNEL DATA -----
            c_resp = requests.get(
                CHANNEL_URL,
                params={
                    "part": "statistics",
                    "id": ",".join(channel_ids),
                    "key": API_KEY
                }
            )

            if c_resp.status_code != 200:
                continue

            channel_lookup = {c["id"]: c for c in c_resp.json().get("items", [])}

            # ----- FILTER LOGIC -----
            for item in items:

                vid = item["id"]["videoId"]
                cid = item["snippet"]["channelId"]

                if vid not in video_lookup or cid not in channel_lookup:
                    continue

                v_obj = video_lookup[vid]
                c_obj = channel_lookup[cid]

                # Duration
                dur_iso = v_obj.get("contentDetails", {}).get("duration")
                if not dur_iso:
                    continue

                duration_min = iso_to_minutes(dur_iso)
                if duration_min < 10:
                    continue

                # Stats
                views = int(v_obj.get("statistics", {}).get("viewCount", 0))
                subs = int(c_obj.get("statistics", {}).get("subscriberCount", 0))

                if views < 2000:
                    continue
                if subs < 1000:
                    continue

                results.append({
                    "Keyword": keyword,
                    "Title": item["snippet"]["title"],
                    "Duration": f"{duration_min} min",
                    "Views": views,
                    "Subscribers": subs,
                    "URL": f"https://www.youtube.com/watch?v={vid}",
                    "Description": item["snippet"].get("description", "")
                })

        # ----- DISPLAY RESULTS -----
        if results:
            results.sort(key=lambda x: x["Views"], reverse=True)
            st.success(f"🚗 Found {len(results)} rare-car viral candidates")

            for r in results:
                st.markdown(f"""
---
## 🚗 {r['Title']}

**Keyword:** {r['Keyword']}  
⏱ {r['Duration']}  
👁 {r['Views']:,} views  
👥 {r['Subscribers']:,} subs  

🔗 [Watch Video]({r['URL']})

{r['Description']}
""")

        else:
            st.warning("No qualifying videos found.")

    except Exception as e:
        st.error(f"❌ Runtime Error: {e}")
