# 🏢 QUOFFICE - The Office Quotes App

### Description
Ever tried to drop a quote from The Office in a text but couldn't quite remember how it went?

Now, just type what you think the line is, and the QUOFFICE will track down the exact quote for you - and show you the conversation around it.

- **Streamlit App**: https://quoffice.streamlit.app/

### Features
- **Forgiving search**: exact matches first, then close matches (≈) for typos and misremembered words - "bears beats battlestar galactica" finds *"Bears. Beets. Battlestar Galactica."*
- **Conversation view**: see the lines before and after the quote, within the same episode
- **Filters**: narrow down by season and character
- **Shareable links**: the search is kept in the URL (`?q=...`)

### Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run quoffice.py
```

### Tests
```bash
pip install pytest
pytest
```

### Project structure
```
quoffice.py        # Streamlit UI (app entry point)
core/
  data.py          # loads the dataset and normalizes text
  search.py        # exact + fuzzy quote search, conversation context
tests/             # pytest tests for core/
data/schrute.csv   # every line of dialogue from the show
```

### Acknowledgments
This project relies heavily on the data provided by the [schrutepy](https://github.com/bradlindblad/schrutepy) Python package.
