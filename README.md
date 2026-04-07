# 🎵 Music Recommender Simulation

## Project Summary

In this project, I built a content-based music recommender system using a database of 65 real-world songs pulled from three distinct, human-curated playlists (Indie Rock, Alt Pop, and Dark Pop). Instead of relying on collaborative filtering (looking at what other users listen to), this system simulates how platforms match tracks based on specific audio features. It represents songs and user taste profiles as data, utilizes a custom mathematical scoring rule to rank the database, and actively mitigates filter bubbles using a dynamic fairness penalty.

---

## How The System Works

Real-world recommendation systems generally use a massive combination of collaborative filtering (user history) and content-based filtering (audio features). My version prioritizes **content-based filtering**. It completely ignores user history and instead acts as a direct matchmaker between a user's stated "vibe" and the mathematical audio features of the songs in the catalog.

Here is a breakdown of the specific data and logic the system relies on:

- **Song Features:** Each `Song` in the database utilizes multiple key attributes:
  - Categorical: `genre`, `mood`, and `decade`
  - Numerical: `energy` (0.0 to 1.0), `danceability` (0.0 to 1.0), and `popularity` (0-100)
- **User Profile:** The `UserProfile` stores the listener's preferences to match against the songs.
- **Scoring Logic & Modes:** The `Recommender` acts as a judge, evaluating each song out of a maximum of 5.0 points. The system features three distinct strategic modes:
  - **DEFAULT:** Balances categorical tags (+0.5 for genre, +1.0 for mood) with mathematical absolute differences for energy, danceability, popularity, and era.
  - **VIBE ONLY:** Completely ignores text tags like genre and mood, ranking songs purely on their physical audio math (energy and danceability).
  - **GENRE HEAVY:** Creates an intentional filter bubble by awarding a massive +3.0 points to an exact genre match.
- **The Fairness Filter (Diversity Penalty):** To prevent the algorithm from filling the Top 5 with songs from the exact same artist, a real-time loop tracks recommendations. If an artist has already been recommended, any subsequent songs by that artist are hit with a **-1.5 point Diversity Penalty**, dynamically pushing them down the rankings to ensure a diverse playlist.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies (now includes tabulate for UI formatting, and spotipy / python-dotenv for API testing):

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python src/main.py
   ```

### Running Tests

Run the tests (expanded from 3 to 13 to cover type hinting, zero-values, and diversity logic) with:

```bash
pytest
```

---

## Experiments I Tried

- **Algorithmic Weight Shifting:** Tested how shifting the weight of genre from +3.0 to +0.5 completely alters the Top 5 rankings, proving how easily developers can trap users in a filter bubble.

- **The Diversity Penalty:** Intentionally loaded the `songs.csv` database with multiple highly-rated tracks by Tate McRae, Taylor Swift, and Olivia Rodrigo to see if the math would recommend them all in a row.  
  **Result:** The -1.5 fairness penalty worked flawlessly, throwing "System Alerts" in the backend and successfully banning duplicate artists from the final output.

- **Attempted Spotify API Integration:** I attempted to upgrade the simulation into a real-world tool by connecting it to the Spotify Web API to harvest live audio features and automatically generate playlists.  
  **Result:** The integration was unsuccessful due to third-party data restrictions. On November 27, 2024, Spotify officially deprecated the `audio-features` and `audio-analysis` endpoints. They locked this mathematical data behind enterprise walls, resulting in a HTTP 403 Forbidden error when trying to fetch the exact energy and danceability scores needed for my algorithm.

---

## Visual Proof

**The Tabulate UI & Diversity Penalty Logs:**  
(Place screenshot of terminal output showing the beautiful ASCII tables and the 🚨 System Alerts here)  
`[Insert Screenshot Here]`

**The Spotify 403 Deprecation Error:**  
(Place screenshot of the terminal throwing the 403 Forbidden error here)  
`[Insert Screenshot Here]`

---

## Limitations and Risks

- **Third-Party Reliance:** As proven by the Spotify API experiment, relying on closed-source APIs for foundational math (like danceability) is highly risky. If a company deprecates an endpoint, the entire recommender breaks.
- **Small Catalog:** It only works on a curated 65-song database.
- **Lack of Lyrical Context:** The algorithm does not understand lyrics or language, relying entirely on assigned numeric values.
