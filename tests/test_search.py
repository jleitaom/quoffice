import pytest

from core.data import load_quotes, normalize
from core.search import get_conversation, search_quotes


@pytest.fixture(scope="module")
def df():
    return load_quotes()


def test_normalize_strips_case_and_punctuation():
    assert normalize("That's what SHE said!") == "thats what she said"
    assert normalize(None) == ""


def test_search_ignores_case_and_punctuation(df):
    results = search_quotes(df, "THATS what she SAID!!")
    assert len(results) > 0
    assert results["normalized_text"].str.contains("thats what she said").all()


def test_search_blank_query_returns_nothing(df):
    assert search_quotes(df, "").empty
    assert search_quotes(df, "?!...").empty


def test_search_returns_duplicate_lines_as_separate_rows(df):
    # Michael says "Whassup!" twice in the Pilot (rows 18 and 20)
    results = search_quotes(df, "whassup")
    michael = results[(results["character"] == "Michael") & (results["text"] == "Whassup!")]
    assert list(michael.index) == [18, 20]


@pytest.mark.parametrize("query, expected_row", [
    ("bears beats battlestar galactica", 12461),            # "Bears. Beets. Battlestar Galactica."
    ("identity theft is not funny", 12464),                 # "Identity theft is not a joke, Jim!"
    ("im not superstitious but im a little stitious", 13963),
])
def test_search_finds_misremembered_quotes(df, query, expected_row):
    results = search_quotes(df, query)
    assert expected_row in results.head(3).index
    assert results.at[expected_row, "match"] == "close"


def test_search_lists_exact_matches_before_close_ones(df):
    results = search_quotes(df, "dwight you ignorant slut")
    assert list(results["match"].iloc[:2]) == ["exact", "exact"]
    assert set(results["match"].iloc[2:]) <= {"close"}


def test_search_ignores_short_lines_that_fit_inside_the_query(df):
    results = search_quotes(df, "identity theft is not funny")
    assert (results["text"].str.len() > 10).all()


def test_search_gibberish_returns_nothing(df):
    assert search_quotes(df, "xqzzv").empty


def test_conversation_is_centered_on_selected_line(df):
    convo = get_conversation(df, 100, 3)
    assert list(convo.index) == list(range(97, 104))


def test_conversation_stays_within_episode(df):
    # Row 228 is the last line of S1E1; row 229 starts S1E2
    convo = get_conversation(df, 228, 3)
    assert list(convo.index) == [225, 226, 227, 228]
    assert (convo["episode"] == 1).all()


def test_conversation_at_start_of_show(df):
    convo = get_conversation(df, 0, 3)
    assert list(convo.index) == [0, 1, 2, 3]
