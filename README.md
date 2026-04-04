<!-- markdownlint-disable MD036 -->
# 🎵 Music Recommender Simulation

## Project Summary

In this project, I built a content-based music recommender system using a database of 45 real-world songs pulled from three distinct, human-curated playlists. Instead of relying on collaborative filtering (looking at what other users listen to), this system simulates how platforms match tracks based on specific audio features. It represents songs and user taste profiles as data, utilizes a custom mathematical scoring rule to rank the database, and helps evaluate how algorithmic weightings can create filter bubbles in real-world applications.

---

## How The System Works

Real-world recommendation systems (like those on Spotify or YouTube) generally use a massive combination of collaborative filtering (user history) and content-based filtering (audio features). My version prioritizes **content-based filtering**. It completely ignores user history and instead acts as a direct matchmaker between a user's stated "vibe" and the mathematical audio features of the songs in the catalog.

Here is a breakdown of the specific data and logic the system relies on:

- **Song Features:** Each `Song` in the database utilizes four key attributes:
  - Categorical: `genre` and `mood`
  - Numerical: `energy` (0.0 to 1.0) and `danceability` (0.0 to 1.0)
- **User Profile:** The `UserProfile` stores the listener's preferences to match against the songs: `favorite_genre`, `favorite_mood`, `target_energy`, and `target_danceability`.
- **Scoring Logic:** The `Recommender` acts as a judge, evaluating each song out of a maximum of 5.0 points based on the following recipe:
  - **+2.0 points** for an exact `genre` match.
  - **+1.0 point** for an exact `mood` match.
  - **Up to +1.0 point** for `energy` similarity (calculated as `1.0` minus the absolute difference between the user's target energy and the song's actual energy).
  - **Up to +1.0 point** for `danceability` similarity (calculated exactly like energy).
- **The Recommendation Process:** To choose the final recommendations, the system loops through every single song in the database, applies the scoring logic to calculate a Relevance Score, and then sorts the entire list from highest to lowest score to deliver the user's Top 5 tracks.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

1. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this

---
