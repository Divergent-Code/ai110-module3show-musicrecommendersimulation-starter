# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

The Dark Vibe Matrix

## 2. Goal / Task

This recommender tries to suggest the top 5 songs that best match a user's specific musical "vibe" by comparing their personal tastes against the mathematical audio features of a music database.

## 3. Data Used

The dataset consists of a 45-song catalog built from three real-world, human-curated playlists. It uses features like `genre`, `mood`, `energy` (0.0-1.0), and `danceability` (0.0-1.0). Because the data is heavily curated from three specific listeners, it is limited in scope and lacks representation from massive global genres like Country, Classical, or Reggaeton.

## 4. Algorithm Summary

The system acts as a judge, scoring every song out of 5.0 possible points. It awards flat points if the song's text tags (genre and mood) exactly match what the user wants. Then, it calculates "similarity points" by finding the mathematical difference between the user's target energy/danceability and the song's actual audio levels. It sorts the final scores from highest to lowest to pick the top 5.

## 5. Observed Behavior / Biases

The initial logic exhibited a severe "filter bubble" bias. Because it awarded a massive +2.0 points for an exact genre match, it over-prioritized songs from the user's favorite genre. It completely ignored fantastic tracks from other genres that actually matched the user's exact energy and danceability preferences.

## 6. Evaluation Process

I tested the system using three distinct user profiles: Rob (Indie Rock), Azalea (Alt Pop), and Onika (Dark Pop/Trap Metal). I then ran a "weight shift" experiment where I lowered the value of a genre match from +2.0 to +0.5. I observed how the recommendations changed when the system was forced to rely on raw audio math instead of text tags.

## 7. Intended Use and Non-Intended Use

**Intended Use:** For classroom exploration to understand how content-based filtering algorithms work, and to demonstrate how algorithmic weights create filter bubbles.
**Non-Intended Use:** This should not be used for commercial deployment or as a production-ready music recommendation engine.

## 8. Ideas for Improvement

1. Allow users to input a list of multiple favorite genres instead of forcing them to pick just one.
2. Add a "Group Session" feature that averages the preferences of multiple users to recommend songs they would all enjoy.
3. Incorporate other available numerical data like `acousticness` to better distinguish the physical sound of the tracks.

---

## 9. Personal Reflection

My biggest learning moment during this project was realizing how easily a developer can accidentally trap a user in a "filter bubble." Just by assigning too many points to a text category like `genre`, the algorithm becomes blinded to other great matches.

Using AI tools was incredibly helpful for quickly formatting my real-world playlists into clean CSV data and generating the Object-Oriented Python logic. However, I had to double-check the AI's math in the `score_song` function to ensure it was actually calculating the absolute differences in energy and danceability correctly based on my specific rules.

I was genuinely surprised by how a simple 5-point math system can actually "feel" like a smart recommendation. During my weight-shift experiment, the algorithm successfully realized that a dark pop song from Onika's playlist shared the exact same mathematical vibe as Azalea's alt-pop tastes and recommended it to her. If I were to extend this project, I would love to connect it to the actual Spotify API to pull real audio features for thousands of songs and see how the math holds up at scale!
