import re

import streamlit as st

from core.data import load_quotes
from core.search import get_conversation, search_quotes

MAX_RESULTS = 50
EXAMPLES = ["bears beats battlestar galactica", "i declare bankrupcy", "identity theft is not funny"]

# Page setup
st.set_page_config(
    page_title="QUOFFICE | The Office Quotes Machine",
    page_icon="🏢",
    layout="wide",
)


# Load and cache data
@st.cache_data
def load_data():
    return load_quotes()


df = load_data()


@st.cache_data
def find_quotes(query, seasons, characters):
    pool = df
    if seasons:
        pool = pool[pool["season"].isin(seasons)]
    if characters:
        pool = pool[pool["character"].isin(characters)]
    return search_quotes(pool, query)


# Escape characters Streamlit markdown would interpret ("$1,200 ... $500" renders as LaTeX otherwise)
def escape_markdown(text):
    return re.sub(r"([\\$*_\[\]`#~<>])", r"\\\1", text)


def quote_label(row):
    prefix = "≈ " if row["match"] == "close" else ""
    return f'{prefix}**{row["character"]}** · S{row["season"]}E{row["episode"]} - {escape_markdown(row["text"])}'


def use_example(text):
    st.session_state.query = text


def clear_query():
    st.session_state.query = ""


# The search lives in the URL (?q=...) so results survive a refresh and can be shared
if "query" not in st.session_state:
    st.session_state.query = st.query_params.get("q", "")


# Sidebar: filters and options
with st.sidebar:
    st.header("Filters")
    seasons = st.multiselect("Season", sorted(df["season"].unique()), placeholder="All seasons")
    characters = st.multiselect(
        "Character", df["character"].value_counts().index, placeholder="Anyone"
    )
    num_context = st.slider("Lines of context", min_value=1, max_value=10, value=3)


# Header and search box
st.title("🏢 QUOFFICE")
st.caption(
    "Ever tried to drop a quote from The Office but couldn't quite remember how it went? "
    "Type the line as you remember it - typos and wrong words are fine."
)
search_col, clear_col = st.columns([12, 1], gap="small", vertical_alignment="center")
query = search_col.text_input(
    "Search quotes",
    key="query",
    placeholder="e.g. bears beats battlestar galactica",
    label_visibility="collapsed",
)
clear_col.button(
    "✕", on_click=clear_query, disabled=not query, help="Clear search", use_container_width=True
)

if query:
    st.query_params["q"] = query
else:
    st.query_params.clear()

# Empty state: offer a few examples
if not query.strip():
    st.write("Not sure where to start? Try one of these:")
    for col, example in zip(st.columns(len(EXAMPLES)), EXAMPLES):
        col.button(example, on_click=use_example, args=(example,), use_container_width=True)
    st.stop()

results = find_quotes(query, tuple(seasons), tuple(characters))
if results.empty:
    st.warning("No quotes found. Try fewer words or remove a filter.")
    st.stop()

# Results summary
num_exact = (results["match"] == "exact").sum()
num_close = len(results) - num_exact
summary = [f"{num_exact:,} exact" if num_exact else "No exact matches", f"{num_close} close (≈)" if num_close else ""]
if len(results) > MAX_RESULTS:
    summary.append(f"showing the first {MAX_RESULTS}, try a longer phrase to narrow it down")
st.caption(" · ".join(part for part in summary if part))

results_col, conversation_col = st.columns([2, 3], gap="large")

# Results list
with results_col:
    shown = results.head(MAX_RESULTS)
    # Radio values are row indices (always unique); labels are display-only
    row_index = st.radio(
        "Choose a quote to see the conversation",
        options=shown.index,
        format_func=lambda i: quote_label(shown.loc[i]),
    )

# Conversation around the selected quote
with conversation_col, st.container(border=True):
    selected = df.loc[row_index]
    st.subheader(selected["episode_name"])
    st.caption(
        f'Season {selected["season"]} · Episode {selected["episode"]} · '
        f'⭐ {selected["imdb_rating"]} IMDb · Aired {selected["air_date"]}  \n'
        f'Written by {selected["writer"].replace(";", ", ")} · Directed by {selected["director"].replace(";", ", ")}'
    )

    for i, line in get_conversation(df, row_index, num_context).iterrows():
        text = escape_markdown(line["text"])
        if i == row_index:
            text = f"**:blue-background[{text}]**"
        with st.chat_message(line["character"]):
            st.markdown(f'**{escape_markdown(line["character"])}**  \n{text}')
