import re
from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "schrute.csv"


# Lowercase and strip punctuation so "That's what she said!" matches "thats what she said"
def normalize(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r"[^\w\s]", "", text.lower())


def load_quotes(path=DATA_PATH):
    # Some rows are stage directions only (no spoken text); they can't be searched or shown
    df = pd.read_csv(path).dropna(subset=["text"])
    df["normalized_text"] = df["text"].apply(normalize)
    return df
