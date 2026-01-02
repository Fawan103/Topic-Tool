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
st.set_page_config(page_title="Philosophy Viral Topics Tool", layout="wide")
st.title("🧠 Philosophy & Consciousness Viral Topics Tool")

days = st.number_input("Enter Days to Search (1–30)", 1, 30, 5)

# ===================================
# PHILOSOPHY / CONSCIOUSNESS KEYWORDS ONLY
# ===================================
keywords = [
    "meaning of life philosophy",
    "consciousness awakening",
    "reality vs illusion",
    "deep truth about existence",
    "existential wisdom",
    "metaphysical truth",
    "human condition",
    "purpose beyond ego",
    "nature of reality philosophy",
    "consciousness explained",
    "perception vs truth",
    "illusion of self",
    "universal consciousness awakening",
    "higher awareness",
    "metaphysics of existence",
    "Plato cave analogy explained",
    "Nietzsche beyond good and evil meaning",
    "Marcus Aurelius meditations wisdom",
    "Stoic philosophy resilience",
    "Epictetus life philosophy",
    "Buddha non-self illusion",
    "Lao Tzu Tao meaning",
    "existential crisis meaning",
    "absurdism Camus explained",
    "free will vs determinism philosophy",
    "identity and self philosophy",
    "philosophy of mind awareness",
    "suffering and meaning",
    "truth nobody tells you about life philosophy",
    "philosophical secrets revealed about existence",
    "deep philosophy you must understand before death",
    "quotes that change how you think",
    "consciousness science philosophy",
    "quantum consciousness meaning",
    "reality explained philosophy meets science",
    "simulation theory philosophy",
    "awakening truth",
    "ancient wisdom decoded",
    "timeless philosophical truths",
    "universal laws of life",
    "wisdom beyond time"
]

# ===================================
# HELPER — ISO DURATION TO MINUTES
# ===================================
def iso_to_minutes(iso: str) -> float:
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
                    "key": API_KEY,
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
                    "key": API_KEY,
                }
            )
            if c_resp.status_code != 200:
                continue
            channel_lookup = {c["id"]: c for c in c_resp.json().get("items", [])}

            # ----- FILTER PIPELINE -----
            for item in items:
                vid = item["id"]["videoId"]
                cid = item["snippet"]["channelId"]

                if vid not in video_lookup or cid not in channel_lookup:
                    continue

                v_obj = video_lookup[vid]
                c_obj = channel_lookup[cid]

                # Duration
                duration_iso = v_obj.get("contentDetails", {}).get("duration")
                if not duration_iso:
                    continue

                duration_min = iso_to_minutes(duration_iso)
                if duration_min < 10:  # duration 10+ minutes
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
            st.success(f"🔥 Found {len(results)} philosophy / consciousness viral candidates")

            for r in results:
                st.markdown(f"""
---
## 🧠 {r['Title']}

**Keyword:** {r['Keyword']}  
⏱ Duration: **{r['Duration']}**  
👁 Views: **{r['Views']:,}**  
👥 Subscribers: **{r['Subscribers']:,}**

🔗 [Watch Video]({r['URL']})

{r['Description']}
""")
        else:
            st.warning("No qualifying videos found with current filters.")

    except Exception as e:
        st.error(f"❌ Runtime Error: {e}")
