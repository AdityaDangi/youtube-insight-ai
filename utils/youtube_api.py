import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime


# =====================================
# YouTube API KEY (from Streamlit Secrets)
# =====================================
API_KEY = st.secrets["YOUTUBE_API_KEY"]


# =====================================
# Build YouTube client
# =====================================
youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)


# =====================================
# Fetch video comments
# =====================================
def get_video_comments(video_id, max_results=500):

    comments = []

    try:

        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            textFormat="plainText"
        )

        response = request.execute()

        while response:

            for item in response["items"]:

                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]

                comments.append({
                    "video_id": video_id,
                    "comment": comment,
                    "timestamp": datetime.now()
                })

            # Stop if limit reached
            if len(comments) >= max_results:
                break

            # Pagination
            if "nextPageToken" in response:

                request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100,
                    pageToken=response["nextPageToken"],
                    textFormat="plainText"
                )

                response = request.execute()

            else:
                break

        print(f"SUCCESS: Fetched {len(comments)} comments")

        return pd.DataFrame(comments)

    except Exception as e:

        print("YouTube API ERROR:", str(e))

        return pd.DataFrame(columns=["video_id", "comment", "timestamp"])


# =====================================
# Fetch video metadata
# =====================================
def get_video_details(video_id):

    try:

        request = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        )

        response = request.execute()

        if not response["items"]:
            return None

        video = response["items"][0]

        return {
            "title": video["snippet"]["title"],
            "channel": video["snippet"]["channelTitle"],
            "views": int(video["statistics"].get("viewCount", 0)),
            "likes": int(video["statistics"].get("likeCount", 0)),
            "comments": int(video["statistics"].get("commentCount", 0))
        }

    except Exception as e:

        print("Video details error:", str(e))
        return None


# =====================================
# Fetch channel videos
# =====================================
def get_channel_videos(channel_name, max_results=10):

    try:

        search_request = youtube.search().list(
            part="snippet",
            q=channel_name,
            type="channel",
            maxResults=1
        )

        search_response = search_request.execute()

        if not search_response["items"]:
            return []

        channel_id = search_response["items"][0]["snippet"]["channelId"]

        videos_request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            type="video",
            order="date",
            maxResults=max_results
        )

        videos_response = videos_request.execute()

        videos = []

        for item in videos_response["items"]:

            videos.append({
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "published": item["snippet"]["publishedAt"]
            })

        print(f"SUCCESS: Found {len(videos)} videos")

        return videos

    except Exception as e:

        print("Channel videos error:", str(e))
        return []


# =====================================
# Fetch channel details
# =====================================
def get_channel_details(channel_name):

    try:

        request = youtube.search().list(
            part="snippet",
            q=channel_name,
            type="channel",
            maxResults=1
        )

        response = request.execute()

        if not response["items"]:
            return None

        channel_id = response["items"][0]["snippet"]["channelId"]

        request = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        )

        response = request.execute()

        channel = response["items"][0]

        return {
            "channel_id": channel_id,
            "title": channel["snippet"]["title"],
            "subscribers": int(channel["statistics"].get("subscriberCount", 0)),
            "total_views": int(channel["statistics"].get("viewCount", 0)),
            "total_videos": int(channel["statistics"].get("videoCount", 0))
        }

    except Exception as e:

        print("Channel details error:", str(e))
        return None