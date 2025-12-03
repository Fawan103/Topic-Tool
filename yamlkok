import streamlit as st import requests
from datetime import datetime, timedelta
# YouTube API Key
API_KEY=" AIzaSyBEkDgN8rmggrbgRSxGznLwrJKkrccWFi0"
YOUTUBE_SEARCH_URL=
"https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL=
"https://www.googleapis.com/youtube/v3/videos*
YOUTUBE_CHANNEL_URL =
"https://www.googleapis.com/youtube/v3/channels"
# Streamlit App Title
st.title ("You Tube Viral Topics Tool")
# Input Fields
days = st.number_input("Enter Days to Search (1-30):". min_value=1,
max_value=30, value=5)
# List of broader keywords
keywords = [
"manifestation", "law of attraction", "spiritual awakening", "ancient prayers", "inner power", "consciousness shift", "mindset transformation", "self-discovery journey", "divine wisdom", "awakening truth", "spiritual growth", "you are divine", "power of belief", "manifest your reality", "subconscious programming", "inner alchemy", "energy healing", "soul journey", "higher consciousness", "awakening path"
]
# Fetch Data Button
if st.button ("Fetch Data"):
if st. button ("Fetch Data"):
try:
# Calculate date range
start date = (datetime.utcnow -
timedelta(days=int(days))).isoformat("T") + "2"
all_results = 0
# Iterate over the list of keywords
for keyword in keywords:
st.write(f"Searching for keyword: {keyword)")
# Define search parameters
search params = {
"part": "snippet",
"9": keyword,
"type": "video",
"order": "viewCount",
"published After": start _date,
"maxResults": 5,
"key": APIKEY,
}
# Fetch video data
response = requests.get(YOUTUBE_SEARCH_URL,
params=search_params)
data = response.json()
# Check if "items" key exists
if "items" not in data or not data("items"]:
st.warning(f"No videos found for keyword: (keyword)") continue
videos = data["items"]
video_ids = [video["id"I"videold"] for video in videos if "id" in video
and "videold" in video["id"])
channel_ids = [video["snippet"["channelld] for video in videos if
"snippet" in video and "channelld" in video"snippet"]]
if not video _ids or not channel _ids:
st.warning(f"Skipping keyword: (keyword) due to missing
video/channel data.")
continue
# Fetch video statistics
stats_params = ["part": "statistics", "id": "."join(video_ids), "key":
APLKEY}
stats_response = requests.get(YOUTUBE_VIDEO_URL.
params=stats_params)
stats_data = stats_response.json()
二・三・三・三三✕
Editing
回
+
3 of 5
if "items" not in stats_data or not stats_data["items": st.warning(f"Failed to fetch video statistics for keyword:
(keyword}")
continue
# Fetch channel statistics
channel_params = ("part": "statistics", "id": "W.join(channel_ids),
"key": AP|KEY}
channel_response = requests.get(YOUTUBE_CHANNEL_URL,
params=channel_params)
channel_data = channel_response.json()
if "items" not in channel_data or not channel_data ["items"]: st.warning (f"Failed to fetch channel statistics for keyword:
(keyword}")
continue
stats = stats_data["items"]
channels = channel_data ["items"
# Collect results
for video, stat, channel in zip(videos, stats, channels):
title = video["snippet"].get("title", "N/A")
description = video["snippet").get("description", 'J:200]
video_url =
f'https://www.youtube.com/watch?v={video[id][videold'])"
views = int(stat["statistics"].get("viewCount", 0))
subs = int(channel["statistics"].get("subscriberCount", 0))
if subs < 3000: # Only include channels with fewer than 3,000
subscribers
all_results.append(f
"Title": title,
"Description": description,
"URL": video _uri,
"Views": views,
"Subscribers": subs
+
# Display results
if all results:
st.success(f"Found {len(all_results)} results across all keywords!") for result in all_results: st.markdown(
f**Title:** (resulti'Title']) In™
***Description:** (result|'Description']} In" f***URL:** [Watch Video]({result'URL]}) In"
f***Views:** (result["Views']) In"
f"**Subscribers:** {result['Subscribers']}"
st.write("---")
else:
subscribers.")
st.warning("No results found for channels with fewer than 3,000
subscribers.")
except Exception as e:
st.error(f"An error occurred: (e}")

