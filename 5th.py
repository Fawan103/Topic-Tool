 import streamlit as st
import requests
from datetime import datetime, timedelta

# ==========================
# CONFIG
# ==========================
API_KEY = " AIzaSyBEkDgN8rmggrbgRSxGznLwrJKkrccWFi0"  # ← put your real key here

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

# ==========================
# MAIN EXECUTION
# ==========================
if st.button("Fetch Data"):
    try:
        # Calculate publishedAfter date in RFC3339 (UTC)
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"

        all_results = []

        for keyword in keywords:
            st.write(f"🔍 Searching for keyword: **{keyword}**")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }

            search_response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)

            if search_response.status_code != 200:
                st.warning(f"Search API error for keyword '{keyword}': {search_response.text}")
                continue

            data = search_response.json()
            items = data.get("items", [])
            if not items:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            # Collect video & channel IDs
            video_ids = [
                item.get("id", {}).get("videoId")
                for item in items
                if item.get("id", {}).get("videoId")
            ]
            channel_ids = [
                item.get("snippet", {}).get("channelId")
                for item in items
                if item.get("snippet", {}).get("channelId")
            ]

            if not video_ids or not channel_ids:
                st.warning(f"Skipping keyword '{keyword}' due to missing video/channel data.")
                continue

            # --------------------------
            # Fetch video statistics
            # --------------------------
            stats_params = {
                "part": "statistics",
                "id": ",".join(video_ids),
                "key": API_KEY,
            }
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            if stats_response.status_code != 200:
                st.warning(f"Video stats API error for keyword '{keyword}': {stats_response.text}")
                continue

            stats_data = stats_response.json()
            stats_items = stats_data.get("items", [])
            if not stats_items:
                st.warning(f"No video statistics found for keyword: {keyword}")
                continue

            stats_by_id = {item["id"]: item for item in stats_items}

            # --------------------------
            # Fetch channel statistics
            # --------------------------
            channel_params = {
                "part": "statistics",
                "id": ",".join(channel_ids),
                "key": API_KEY,
            }
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            if channel_response.status_code != 200:
                st.warning(f"Channel stats API error for keyword '{keyword}': {channel_response.text}")
                continue

            channel_data = channel_response.json()
            channel_items = channel_data.get("items", [])
            if not channel_items:
                st.warning(f"No channel statistics found for keyword: {keyword}")
                continue

            channels_by_id = {item["id"]: item for item in channel_items}

            # --------------------------
            # Collect results
            # --------------------------
            for item in items:
                video_id = item.get("id", {}).get("videoId")
                snippet = item.get("snippet", {})
                channel_id = snippet.get("channelId")

                if not video_id or not channel_id:
                    continue

                stat = stats_by_id.get(video_id)
                channel = channels_by_id.get(channel_id)

                if not stat or not channel:
                    continue

                title = snippet.get("title", "N/A")
                description = snippet.get("description", "N/A")
                video_url = f"https://www.youtube.com/watch?v={video_id}"

                view_count_str = stat.get("statistics", {}).get("viewCount", "0")
                sub_count_str = channel.get("statistics", {}).get("subscriberCount", "0")

                try:
                    views = int(view_count_str)
                except (TypeError, ValueError):
                    views = 0

                try:
                    subs = int(sub_count_str)
                except (TypeError, ValueError):
                    subs = 0

                # Only include channels with fewer than 3,000 subscribers
                if subs < 3000:
                    all_results.append(
                        {
                            "Keyword": keyword,
                            "Title": title,
                            "Description": description,
                            "URL": video_url,
                            "Views": views,
                            "Subscribers": subs,
                        }
                    )

        # ==========================
        # DISPLAY RESULTS
        # ==========================
        if all_results:
            # Sort by views descending
            all_results = sorted(all_results, key=lambda x: x["Views"], reverse=True)

            st.success(
                f"✅ Found {len(all_results)} results across all keywords (channels < 3,000 subs)."
            )

            for result in all_results:
                st.markdown(
                    f"""---
**Keyword:** {result['Keyword']}  
**Title:** {result['Title']}  

**Description:**  
{result['Description']}

**URL:** [Watch Video]({result['URL']})  
**Views:** {result['Views']:,}  
**Subscribers:** {result['Subscribers']:,}
"""
                )
        else:
            st.warning("No results found for channels with fewer than 3,000 subscribers.")

    except Exception as e:
        # Note: keep this on a single line so the f-string is not broken
        st.error(f"❌ Runtime error: {e}")
