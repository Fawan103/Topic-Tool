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
st.set_page_config(page_title="Sad Love Songs Viral Tool", layout="wide")
st.title("💔 Sad Love Songs & Heartbreak Viral Topics Tool")

days = st.number_input("Enter Days to Search (1–30)", 1, 30, 5)

# ===================================
# SAD LOVE / HEARTBREAK SONGS KEYWORDS (NEW LIST ONLY)
# ===================================
keywords = [
    "sad love songs",
    "heartbreaking love songs",
    "emotional love song lyrics",
    "deep sad songs",
    "missing you songs",
    "i miss you love song",
    "heartbreak songs 2025",
    "emotional breakup songs",
    "love lost songs",
    "sad romantic ballads",
    "soul touching love songs",
    "crying love songs",
    "songs about letting go",
    "songs about still loving someone",
    "unrequited love songs",
    "goodbye love songs",
    "pain of lost love",
    "emotional male version songs",
    "heartfelt sad songs",
    "love songs that hurt",
    "songs about waiting for love",
    "love that faded away",
    "silent heartbreak songs",
    "songs about loving her forever",
    "still yours love song",
    "empty without you song",
    "love songs about absence",
    "songs about betrayal and broken trust",
    "emotional slow songs",
    "sad English love songs with lyrics",
    "official lyrics love songs",
    "heartbreak music 2025",
    "romantic sad ballads",
    "deep emotional music",
    "love songs for late night",
    "soul blues heartbreak",
    "emotional music for missing someone",
    "love songs about regret",
    "songs about loving without being loved back",
    "quiet cry love songs",
    "love songs that feel real",
    "emotional songs that make you cry"
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

            if not video_ids or not channel_ids:
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
                # ✅ 3+ minutes instead of 10+
                if duration_min < 3:
                    continue

                # Stats
                v_stats = v_obj.get("statistics", {})
                c_stats = c_obj.get("statistics", {})

                try:
                    views = int(v_stats.get("viewCount", 0))
                except (TypeError, ValueError):
                    views = 0

                try:
                    subs = int(c_stats.get("subscriberCount", 0))
                except (TypeError, ValueError):
                    subs = 0

                # Filters: 2k+ views, 1k+ subs
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

        # ===================================
        # DISPLAY RESULTS
        # ===================================
        if results:
            results.sort(key=lambda x: x["Views"], reverse=True)
            st.success(f"💔 Found {len(results)} sad love song viral candidates")

            for r in results:
                st.markdown(f"""
---
## 💔 {r['Title']}

**Keyword:** {r['Keyword']}  
⏱ Duration: **{r['Duration']}**  
👁 Views: **{r['Views']:,}**  
👥 Subscribers: **{r['Subscribers']:,}**

🔗 [Watch Video]({r['URL']})

{r['Description']}
""")
        else:
            st.warning("No qualifying sad love songs found with current filters.")

    except Exception as e:
        st.error(f"❌ Runtime Error: {e}")
