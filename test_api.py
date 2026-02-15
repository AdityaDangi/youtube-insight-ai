from utils.youtube_api import get_video_comments

video_id = "ERCMXc8x7mc"

df = get_video_comments(video_id)

print("Comments fetched:", len(df))
print(df.head())