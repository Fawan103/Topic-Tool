import streamlit as st
import requests
from datetime import datetime, timedelta

# ==========================
# CONFIG
# ==========================
API_KEY = " AIzaSyBEkDgN8rmggrbgRSxGznLwrJKkrccWFi0"

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# ==========================
# UI
# ==========================
st.title("📊 YouTube Viral Topics Tool")

days = st.number_input(
    "Enter days to look back:",
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
    "self discovery journey",
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
# EXECUTION
# ==========================
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
                "maxResults": 5,
                "publishedAfter": start_date,
                "key": API_KEY,
            }

            resp = requests.get(SEARCH_URL, params=params)
            items = resp.json().get("items", [])

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

            # --------------------
            # Video statistics
            # --------------------
            v_params = {
                "part": "statistics",
                "id": ",".join(video_ids),
                "key": API_KEY
            }

            v_resp = requests.get(VIDEO_URL, params=v_params)
            v_stats = {
                v["id"]: v
                for v in v_resp.json().get("items", [])
            }

            # --------------------
            # Channel statistics
            # --------------------
            c_params = {
                "part": "statistics",
                "id": ",".join(channel_ids),
                "key": API_KEY
            }

            c_resp = requests.get(CHANNEL_URL, params=c_params)
            c_stats = {
                c["id"]: c
                for c in c_resp.json().get("items", [])
            }

            # --------------------
            # Create rows
            # --------------------
            for item in items:

                video_id = item["id"]["videoId"]
                channel_id = item["snippet"]["channelId"]

                if (
                    video_id not in v_stats or
                    channel_id not in c_stats
                ):
                    continue

                title = item["snippet"]["title"]
                desc = item["snippet"]["description"]

                views = int(
                    v_stats[video_id]["statistics"].get("viewCount", 0)
                )

                subs = int(
                    c_stats[channel_id]["statistics"]
                    .get("subscriberCount", 0)
                )

                if subs < 3000:
                    results.append({
                        "keyword": keyword,
                        "title": title,
                        "description": desc,
                        "views": views,
                        "subs": subs,
                        "url": f"https://www.youtube.com/watch?v={video_id}"
                    })

        # ==========================
        # DISPLAY
        # ==========================
        if results:
            results.sort(key=lambda x: x["views"], reverse=True)

            st.success(f"✅ {len(results)} qualifying videos found")

            for row in results:
                st.markdown(f"""
---
### {row['title']}
**Keyword:** {row['keyword']}

👁️ Views: {row['views']:,}  
👥 Subs: {row['subs']:,}

🔗 [Watch Video]({row['url']})

{row['description']}
""")
        else:
            st.warning("No videos met your criteria.")

    except Exception as e:
        st.error(f"❌ Runtime
