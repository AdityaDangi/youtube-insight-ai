import pandas as pd
import numpy as np


def analyze_comments(df):

    df["length"] = df["comment"].apply(len)

    total = len(df)

    avg_length = np.mean(df["length"])

    median_length = np.median(df["length"])

    max_length = np.max(df["length"])

    min_length = np.min(df["length"])

    analysis = {

        "total_comments": total,
        "average_length": avg_length,
        "median_length": median_length,
        "max_length": max_length,
        "min_length": min_length

    }

    return analysis