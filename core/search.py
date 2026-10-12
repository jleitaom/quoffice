import pandas as pd
from rapidfuzz import fuzz, process

from core.data import normalize

# Close matches must score at least this (0-100) to be shown
FUZZY_MIN_SCORE = 75
# Max close matches to add; also, fuzzy search only runs when there are fewer exact matches than this
FUZZY_LIMIT = 20
# Lines much shorter than the query (e.g. "No.") would fit inside it and score 100, so skip them
MIN_LENGTH_RATIO = 0.75


def search_quotes(df, query):
    """Exact matches first (in episode order), then close matches ranked by similarity.

    Adds a `match` column: "exact" or "close".
    """
    query = normalize(query).strip()
    if not query:
        return df.iloc[0:0]

    exact = df[df["normalized_text"].str.contains(query, regex=False)].assign(match="exact")
    if len(exact) >= FUZZY_LIMIT:
        return exact

    long_enough = df["normalized_text"].str.len() >= MIN_LENGTH_RATIO * len(query)
    pool = df.loc[long_enough & ~df.index.isin(exact.index), "normalized_text"]
    hits = process.extract(
        query, pool, scorer=fuzz.partial_ratio, score_cutoff=FUZZY_MIN_SCORE, limit=FUZZY_LIMIT
    )
    close = df.loc[[row_index for _, _, row_index in hits]].assign(match="close")

    return pd.concat([exact, close])


def get_conversation(df, row_index, num_context):
    """Return the selected line plus up to `num_context` lines either side, within the same episode."""
    selected = df.loc[row_index]
    episode = df[(df["season"] == selected["season"]) & (df["episode"] == selected["episode"])]
    pos = episode.index.get_loc(row_index)

    start = max(0, pos - num_context)
    end = min(len(episode), pos + num_context + 1)
    return episode.iloc[start:end]
