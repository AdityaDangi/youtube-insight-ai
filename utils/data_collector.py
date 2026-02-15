import pandas as pd
import datetime
import os

from utils.youtube_api import get_video_comments
from utils.db_manager import insert_comments
from utils.predict import predict_sentiment   # ✅ IMPORTANT


def collect_and_save_comments(video_id):

    print("Fetching comments from YouTube API...")

    # =====================================
    # Fetch comments from API
    # =====================================
    df = get_video_comments(video_id)

    # Handle empty case
    if df is None or len(df) == 0:
        print("No comments found.")
        return None, None


    # =====================================
    # Ensure required columns exist
    # =====================================
    if "timestamp" not in df.columns:
        df["timestamp"] = datetime.datetime.now()


    # =====================================
    # ✅ REAL SENTIMENT ANALYSIS (FIX)
    # =====================================
    print("Running sentiment analysis...")

    df["sentiment"] = df["comment"].apply(
        lambda comment: predict_sentiment(str(comment))
    )


    print("Sentiment analysis completed.")


    # =====================================
    # Create data folder if not exists
    # =====================================
    os.makedirs("data", exist_ok=True)


    # =====================================
    # Save individual video dataset
    # =====================================
    filename = f"data/comments_{video_id}.csv"

    df.to_csv(filename, index=False)

    print(f"Saved individual dataset: {filename}")


    # =====================================
    # Save master dataset
    # =====================================
    master_file = "data/master_dataset.csv"

    try:

        master_df = pd.read_csv(master_file)

        master_df = pd.concat(
            [master_df, df],
            ignore_index=True
        )

    except FileNotFoundError:

        master_df = df


    master_df.to_csv(master_file, index=False)

    print("Updated master_dataset.csv")


    # =====================================
    # Save to SQL database
    # =====================================
    try:

        insert_comments(df)

        print("Inserted data into SQL database")

    except Exception as e:

        print("Database insert failed:", str(e))


    # =====================================
    # Show summary
    # =====================================
    positive = (df["sentiment"] == "positive").sum()
    negative = (df["sentiment"] == "negative").sum()

    print(f"Positive comments: {positive}")
    print(f"Negative comments: {negative}")
    print(f"Total comments: {len(df)}")


    # =====================================
    # Return dataframe and filename
    # =====================================
    return df, filename