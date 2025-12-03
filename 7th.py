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

                # Filter: channels under 3k subs only
                if subs < 3000:
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

            st.success(f"✅ Found {len(results)} viral candidates")

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
