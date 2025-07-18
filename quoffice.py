import streamlit as st
import pandas as pd
import re

# Page setup
st.set_page_config(
    page_title="QUOFFICE | The Office Quotes Machine",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# App UI
st.sidebar.header("QUOFFICE | The Office Quotes Machine")
st.sidebar.info(
    "Ever tried to drop a quote from The Office but couldn't quite remember how it went? \n\n"
    "Now, just start typing what you think the line is, and the **QUOFFICE** will track down the exact quote for you.\n\n"
    "To use it:\n"
    "- Start typing the line below, the table on top will find all matches\n\n"
    "- Once you find the line, choose it and the entire conversation will come up"
)

# Normalize function to clean text
def normalize(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r"[^\w\s]", "", text.lower())

# Load and cache data
@st.cache_data
def load_data():
    df = pd.read_csv("./data/schrute.csv", sep=",")
    df["normalized_text"] = df["text"].apply(normalize)
    return df

df = load_data()

# Initialize session state
for state in ["search_results", "quote_options", "quote_index_map"]:
    st.session_state.setdefault(state, None)

# Safe default for selected quote index
row_index = None

# Search form in sidebar
with st.sidebar.form("search_form"):
    search_input = st.text_input("Enter a keyword or phrase to search for quotes:")
    submitted = st.form_submit_button("Search")


# Slider to control context range
num_context = st.sidebar.slider(
        "Context range",
        min_value=1,
        max_value=10,
        value=3, 
    )

# Search processing and results in main container
with st.expander("**Quotes**", expanded=True):
    if submitted and search_input:
        normalized_input = normalize(search_input)
        results = df[df["normalized_text"].str.contains(normalized_input, na=False)]

        if results.empty:
            st.warning("No quotes found.")
            for key in ["search_results", "quote_options", "quote_index_map"]:
                st.session_state[key] = None
        else:
            # Create radio options and index mapping
            options = []
            index_map = {}
            for i, row in results.iterrows():
                label = f'**{row["character"]} (S{row["season"]}E{row["episode"]})** - {row["text"]}'
                options.append(label)
                index_map[label] = i

            st.session_state.search_results = results
            st.session_state.quote_options = options
            st.session_state.quote_index_map = index_map

    if all([
        st.session_state.search_results is not None,
        st.session_state.quote_options,
        st.session_state.quote_index_map
    ]):
        selected = st.radio("Choose a quote below to see the conversation", st.session_state.quote_options)
        row_index = st.session_state.quote_index_map.get(selected)
    
    elif search_input == "":
        st.warning("Please enter a keyword or phrase to search for quotes.")


# Context quote display
with st.container(border=True):

    if row_index is not None:
        full_df_index = df.index.get_loc(row_index)

        start = max(0, full_df_index - num_context)
        end = min(len(df), full_df_index + num_context + 1)

        surrounding_quotes = df.iloc[start:end]

        st.markdown(
            f"""
            **{df['episode_name'][row_index]}** |
            **Season {df['season'][row_index]} Ep. {df['episode'][row_index]}** |
            **IMDB Rating {df['imdb_rating'][row_index]}** |
            **Air Date {df['air_date'][row_index]}** 
            """
        )

        for i, row in surrounding_quotes.iterrows():
            is_selected = row.name == row_index

            text = f"***{row['text']}***" if is_selected else row['text']
            character = f"***{row['character']}***" if is_selected else row['character']

            st.markdown(
                f'\n\n>{character}: {text}'
            )