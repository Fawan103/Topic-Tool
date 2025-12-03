import streamlit as st
import requests
from datetime import datetime, timedelta

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
st.set_page_config(page_title="YouTube Viral Topics Tool", layout="wide")

st.title("📊 YouTube Viral Topics Tool")

days = st.number_input(
    "Enter Days to Search (1–30)",
    min_value=1,
    max_value=30,
    value=5,
    step=1
)

# ===================================
# KEYWORDS
# ===================================
keywords = [
    "Reality hack",
    "consciousness hack",
    "words shape reality",
    "power of language",
    "mind conditioning",
    "brain reprogramming",
    "social programming",
    "break the matrix",
    "layers of existence",
    "levels of reality",
    "hidden dimensions",
    "multidimensional consciousness",
    "existential freedom",
    "burden of freedom",
    "existential crisis",
    "search for meaning",
    "purpose of life",
    "why we exist",
    "illusion of time",
    "time is not real",
    "memory and identity",
    "who am I really",
    "ego death",
    "self identity",
    "consciousness and brain",
    "neurophilosophy",
    "manifestation science",
    "divine power within",
    "inner god",
    "self mastery",
    "law of attraction explained",
    "quantum consciousness",
    "observer effect reality",
    "frequency and vibration",
    "ancient wisdom modern science",
    "esoteric philosophy",
    "mystical philosophy",
    "hermetic teachings",
    "secret knowledge",
    "forgotten wisdom",
    "spiritual awakening",
    "dark night of the soul",
    "shadow self",
    "collective unconscious",
    "jungian psychology",
    "philosophy of meaning",
    "nihilism explained",
    "anxiety and the void",
    "fear of existence",
    "self liberation",
    "transcendence",
    "reality and perception",
    "simulation theory",
    "free will vs fate",
    "destiny versus choice",
    "power of belief",
    "subconscious mind",
    "reprogramming reality",
    "emotional conditioning",
    "mental alchemy",
    "higher self awakening",
    "cosmic consciousness",
    "awakening consciousness"
]

# ===================================
# MAIN EXECUTION
# ===================================
if st.button("Fetch Data"):

    try:
        start_date = (
            datetime.utcnow() - timedelta(days=int(days))
        ).isoformat("T") + "Z"

        results = []

        for keyword in keywords:
            st.write(f"🔍 Searching: {keyword}")

            params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }

            search_resp = requests.get(SEARCH_URL, params=params)

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

            # ----------------------------------
            # VIDEO STATS
            # ----------------------------------
            v_params = {
                "part": "statistics",
                "id": ",".join(video_ids),
                "key": API_KEY,
            }

            v_resp = requests.get(VIDEO_URL, params=v_params)
            v_data = v_resp.json()

            video_lookup = {
                v["id"]: v
                for v in v_data.get("items", [])
            }

            # ----------------------------------
            # CHANNEL STATS
            # ----------------------------------
            c_params = {
                "part": "statistics",
                "id": ",".join(channel_ids),
                "key": API_KEY,
            }

            c_resp = requests.get(CHANNEL_URL, params=c_params)
            c_data = c_resp.json()

            channel_lookup = {
                c["id"]: c
                for c in c_data.get("items", [])
            }

            # ----------------------------------
            # BUILD RESULTS
            # ----------------------------------
            for item in items:

                video_id = item["id"]["videoId"]
                channel_id = item["snippet"]["channelId"]

                if video_id not in video_lookup:
                    continue
                if channel_id not in channel_lookup:
                    continue

                title = item["snippet"]["title"]
                description = item["snippet"].get("description", "")
                url = f"https://www.youtube.com/watch?v={video_id}"

                views = int(
                    video_lookup[video_id]["statistics"].get("viewCount", 0)
                )

                subs = int(
                    channel_lookup[channel_id]["statistics"].get("subscriberCount", 0)
                )

                # ✅ UPDATED FILTER — 70K SUB LIMIT
                if subs < 70000:
                    results.append({
                        "Keyword": keyword,
                        "Title": title,
                        "Description": description,
                        "Views": views,
                        "Subscribers": subs,
                        "URL": url
                    })

        # ===================================
        # DISPLAY RESULTS
        # ===================================
        if results:

            results.sort(
                key=lambda x: x["Views"],
                reverse=True
            )

            st.success(f"✅ Found {len(results)} viral candidates (Channels < 70K subs)")

            for r in results:
                st.markdown(
                    f"""
---
### 🔥 {r['Title']}
**Keyword:** {r['Keyword']}

👁️ Views: **{r['Views']:,}**  
👥 Subscribers: **{r['Subscribers']:,}**

🔗 [Watch Video]({r['URL']})

{r['Description']}
"""
                )

        else:
            st.warning("No qualifying videos found.")

    except Exception as e:
        st.error(f"❌ Runtime Error: {e}")
