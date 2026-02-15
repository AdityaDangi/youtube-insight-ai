# =====================================
# FIX: Connect project root to Streamlit
# =====================================
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# =====================================
# Imports
# =====================================
import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import datetime

from utils.youtube_api import get_video_details
from utils.predict import predict_sentiment
from utils.data_collector import collect_and_save_comments
from utils.data_analysis import analyze_comments
from utils.db_manager import fetch_all_comments, insert_comments


# =====================================
# Page Configuration
# =====================================
st.set_page_config(
    page_title="YouTube Insight Engine",
    page_icon="📊",
    layout="wide"
)


# =====================================
# Extract video ID safely
# =====================================
def extract_video_id(url):

    try:

        if "v=" in url:
            return url.split("v=")[1].split("&")[0]

        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]

        elif "embed/" in url:
            return url.split("embed/")[1].split("?")[0]

        else:
            return None

    except:
        return None


# =====================================
# Sidebar Navigation
# =====================================
st.sidebar.title("📊 YouTube Insight Engine")

page = st.sidebar.selectbox(
    "Navigation",
    [
        "Dashboard",
        "Channel Analytics",
        "Video Comparison",
        "Dataset Explorer",
        "Database Explorer",
        "Analysis History",
        "About Project"
    ]
)


# =====================================
# Save Analysis History
# =====================================
def save_history(video_url, positive, negative, total):

    data = {
        "Date": datetime.datetime.now(),
        "Video URL": video_url,
        "Total Comments": total,
        "Positive": positive,
        "Negative": negative
    }

    df = pd.DataFrame([data])

    history_file = os.path.join(PROJECT_ROOT, "data", "history.csv")

    try:

        history = pd.read_csv(history_file)

        history = pd.concat([history, df], ignore_index=True)

    except:

        history = df

    history.to_csv(history_file, index=False)


# =====================================
# DASHBOARD PAGE
# =====================================
if page == "Dashboard":

    st.title("📊 YouTube Video Analytics Dashboard")

    video_url = st.text_input("Enter YouTube Video URL")

    if st.button("Run Full Analysis"):

        video_id = extract_video_id(video_url)

        if video_id is None:

            st.error("Invalid YouTube URL")
            st.stop()


        # =====================================
        # VIDEO METADATA
        # =====================================
        video_info = get_video_details(video_id)

        if video_info:

            st.subheader("📺 Video Information")

            st.write("Title:", video_info["title"])
            st.write("Channel:", video_info["channel"])

            col_meta1, col_meta2, col_meta3 = st.columns(3)

            col_meta1.metric("Views", f"{video_info['views']:,}")
            col_meta2.metric("Likes", f"{video_info['likes']:,}")
            col_meta3.metric("Comments", f"{video_info['comments']:,}")


        # =====================================
        # COLLECT COMMENTS
        # =====================================
        with st.spinner("Collecting comments from YouTube..."):

            df_collected, filename = collect_and_save_comments(video_id)

        if df_collected is None or len(df_collected) == 0:

            st.error("No comments found")
            st.stop()

        st.success(f"Dataset saved: {filename}")


        # =====================================
        # SENTIMENT ANALYSIS
        # =====================================
        with st.spinner("Running sentiment analysis..."):

            df_collected["sentiment"] = df_collected["comment"].apply(predict_sentiment)


        # =====================================
        # UPDATE MASTER DATASET
        # =====================================
        master_file = os.path.join(PROJECT_ROOT, "data", "master_dataset.csv")

        try:

            master_df = pd.read_csv(master_file)

            master_df = master_df[master_df["video_id"] != video_id]

            master_df = pd.concat([master_df, df_collected], ignore_index=True)

        except:

            master_df = df_collected

        master_df.to_csv(master_file, index=False)


        # =====================================
        # UPDATE SQL DATABASE
        # =====================================
        try:

            insert_comments(df_collected)

            st.success("Database updated with sentiment")

        except Exception as e:

            st.warning(f"Database update failed: {e}")


        # =====================================
        # DATASET STATISTICS
        # =====================================
        analysis = analyze_comments(df_collected)

        st.subheader("📈 Dataset Statistics")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Comments", analysis["total_comments"])
        col2.metric("Average Length", round(analysis["average_length"], 2))
        col3.metric("Median Length", round(analysis["median_length"], 2))


        # =====================================
        # SENTIMENT OVERVIEW
        # =====================================
        sentiment_counts = df_collected["sentiment"].value_counts()

        positive = sentiment_counts.get("positive", 0)
        negative = sentiment_counts.get("negative", 0)
        total = len(df_collected)

        save_history(video_url, positive, negative, total)

        st.subheader("📊 Sentiment Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total", total)
        col2.metric("Positive", positive)
        col3.metric("Negative", negative)


        # =====================================
        # PIE CHART
        # =====================================
        st.subheader("Sentiment Distribution")

        fig = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            hole=0.4
        )

        st.plotly_chart(fig, use_container_width=True)


        # =====================================
        # TIMELINE CHART
        # =====================================
        st.subheader("Sentiment Timeline")

        df_collected["index"] = range(len(df_collected))

        fig_line = px.line(
            df_collected,
            x="index",
            y=df_collected["sentiment"].map({"positive": 1, "negative": 0})
        )

        st.plotly_chart(fig_line, use_container_width=True)


        # =====================================
        # WORD CLOUD
        # =====================================
        st.subheader("WordCloud")

        text = " ".join(df_collected["comment"].astype(str))

        wc = WordCloud(
            width=800,
            height=400,
            background_color="black"
        ).generate(text)

        fig_wc, ax = plt.subplots()

        ax.imshow(wc)
        ax.axis("off")

        st.pyplot(fig_wc)


        # =====================================
        # DATASET VIEW
        # =====================================
        st.subheader("Dataset Explorer")

        st.dataframe(df_collected, use_container_width=True)


        # =====================================
        # DOWNLOAD REPORT
        # =====================================
        csv = df_collected.to_csv(index=False)

        st.download_button(
            "Download Report",
            csv,
            "youtube_analysis_report.csv"
        )


# =====================================
# CHANNEL ANALYTICS
# =====================================
elif page == "Channel Analytics":

    st.title("📺 Channel Analytics")

    df = fetch_all_comments()

    if df.empty:

        st.warning("No database data found")
        st.stop()

    sentiment_counts = df["sentiment"].value_counts()

    fig = px.pie(
        values=sentiment_counts.values,
        names=sentiment_counts.index
    )

    st.plotly_chart(fig, use_container_width=True)

    video_counts = df["video_id"].value_counts()

    fig2 = px.bar(
        x=video_counts.index,
        y=video_counts.values,
        labels={"x": "Video ID", "y": "Comments"}
    )

    st.plotly_chart(fig2, use_container_width=True)


# =====================================
# VIDEO COMPARISON
# =====================================
elif page == "Video Comparison":

    st.title("📊 Video Comparison")

    df = fetch_all_comments()

    if df.empty:

        st.warning("No data found")
        st.stop()

    comparison = df.groupby(
        ["video_id", "sentiment"]
    ).size().reset_index(name="count")

    fig = px.bar(
        comparison,
        x="video_id",
        y="count",
        color="sentiment",
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True)


# =====================================
# DATASET EXPLORER
# =====================================
elif page == "Dataset Explorer":

    st.title("Dataset Explorer")

    file = os.path.join(PROJECT_ROOT, "data", "master_dataset.csv")

    if os.path.exists(file):

        df = pd.read_csv(file)

        st.dataframe(df)

    else:

        st.warning("No dataset found")


# =====================================
# DATABASE EXPLORER
# =====================================
elif page == "Database Explorer":

    st.title("Database Explorer")

    df = fetch_all_comments()

    if df.empty:

        st.warning("Database empty")

    else:

        st.dataframe(df)


# =====================================
# HISTORY
# =====================================
elif page == "Analysis History":

    st.title("Analysis History")

    file = os.path.join(PROJECT_ROOT, "data", "history.csv")

    if os.path.exists(file):

        df = pd.read_csv(file)

        st.dataframe(df)

    else:

        st.warning("No history found")


# =====================================
# ABOUT PAGE
# =====================================
elif page == "About Project":

    st.title("YouTube Insight Engine")

    st.write("""
    Professional AI-powered YouTube Analytics Platform

    Features:

    • Video Analytics  
    • Channel Analytics  
    • Sentiment Analysis  
    • SQL Database Integration  
    • Multi-Video Comparison  
    • WordCloud Visualization  
    • Timeline Analytics  
    • Dataset Export  

    Built with:

    Python, Streamlit, Pandas, Plotly, Machine Learning, YouTube API
    """)