# 🎧 Model Card: The Dark Vibe Matrix

## 1. Model Name

The Dark Vibe Matrix

## 2. Goal / Task

This recommender tries to suggest the top 5 songs that best match a user's specific musical "vibe" by comparing their personal tastes against the mathematical audio features of a music database.

## 3. Data Used

The dataset consists of a 65-song catalog built from three real-world, human-curated playlists (Indie Rock, Alt Pop, and Dark Pop/Trap Metal). It uses features like `genre`, `mood`, `decade`, `popularity`, `energy` (0.0-1.0), and `danceability` (0.0-1.0). Because the data is heavily curated from three specific listeners, it is limited in scope and lacks representation from massive global genres like Country or Classical.

## 4. Algorithm Summary

The system acts as a judge, scoring every song out of a possible 5.0 points. It features three dynamic modes:

- **DEFAULT:** Awards balanced points for genre/mood matches, and calculates "similarity points" by finding the absolute mathematical difference between the user's target energy/danceability/popularity and the song's actual levels.
- **VIBE ONLY:** Completely ignores text tags (genre/mood) and scores solely on physical audio math.
- **GENRE HEAVY:** Creates an intentional filter bubble by prioritizing a +3.0 score for exact genre matches.

The system sorts the scores from highest to lowest. Before finalizing the Top 5, it runs a **Fairness Filter**: if the algorithm selects an artist that is already on the recommended list, it applies a `-1.5` Diversity Penalty to prevent artist monopolization.

## 5. Observed Behavior / Biases

The initial logic exhibited two distinct biases. First, a severe "filter bubble" bias where over-prioritizing the genre tag blinded the algorithm to cross-genre matches. Second, an "artist monopoly" bias. Because artists generally write songs with identical mathematical vibes (e.g., Tate McRae or Billie Eilish), the pure math naturally tried to fill the Top 5 list with tracks from a single artist. The implemented diversity penalty successfully countered this.

## 6. Evaluation Process

I tested the system using three distinct user profiles: Rob (Indie Rock), Azalea (Alt Pop), and Onika (Dark Pop). I ran weight-shift experiments to see how recommendations changed when forced to rely on raw audio math versus text tags. To test the diversity penalty, I intentionally bloated the database with duplicate artists and expanded the requested output list (`k=15`) to visually track the algorithm applying the `-1.5` penalty in real-time via terminal system alerts.

## 7. Intended Use and Non-Intended Use

**Intended Use:** For classroom exploration to understand how content-based filtering algorithms work, how algorithmic weights create filter bubbles, and how dynamic loops can enforce playlist fairness.
**Non-Intended Use:** This should not be used for commercial deployment or as a production-ready music recommendation engine.

## 8. Ideas for Improvement

1. **Local Data Processing:** Since public access to major `audio-features` endpoints was deprecated, future iterations should integrate a local audio analysis library (like `librosa`) to calculate BPM and energy from raw MP3 files natively, removing reliance on closed third-party APIs.
2. Add a "Group Session" feature that averages the preferences of multiple users to recommend songs they would all enjoy.
3. Allow users to input a list of multiple favorite genres instead of forcing them to pick just one.

---

## 9. Personal Reflection

My biggest learning moment during this project was realizing how easily a developer can accidentally trap a user in a "filter bubble." Just by assigning too many points to a text category like `genre`, the algorithm becomes blinded to other great matches. Building the diversity penalty taught me that "fairness" in algorithms requires active intervention—the math naturally wanted to spam the same artist until I wrote code to explicitly stop it.

Using AI tools was incredibly helpful for quickly refactoring the code, adding Python `TypedDict` for type hinting, and expanding the test suite to cover edge cases. However, the most jarring lesson came from the real world: I attempted to connect this algorithm to a major streaming platform's Web API, only to discover they locked down their audio-features math behind an enterprise wall in November 2024. It was a stark reminder that even the best code in the world is useless if you don't control the underlying data.
