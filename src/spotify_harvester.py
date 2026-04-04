"""
Spotify Data Harvester - Audio Features Extractor.

This module provides a command-line interface for fetching song metadata
and audio features from the Spotify Web API. It formats the data as CSV
rows for import into the recommendation system.

DEV NOTE: Spotify deprecated their Audio Features API in 2024. This script
includes fallback handling for when the API returns 403 errors. In such
cases, default proxy values are used and the user is instructed to manually
update the values in the generated CSV.

Usage:
    python -m src.spotify_harvester
    python src/spotify_harvester.py

Environment Variables:
    SPOTIPY_CLIENT_ID: Spotify API client ID (required)
    SPOTIPY_CLIENT_SECRET: Spotify API client secret (required)
"""

import os
import sys
from pathlib import Path
from typing import Final

# Add project root to PYTHONPATH for direct script execution
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


# =============================================================================
# CONSTANTS
# =============================================================================
# DEV NOTE: These are default fallback values when Spotify API is unavailable.
# The Audio Features API was deprecated in 2024, so these defaults prevent
# the script from crashing while allowing manual data entry.

# Default audio feature values (neutral midpoints)
DEFAULT_ENERGY: Final[float] = 0.50
DEFAULT_DANCEABILITY: Final[float] = 0.50
DEFAULT_TEMPO_BPM: Final[int] = 120
DEFAULT_VALENCE: Final[float] = 0.50
DEFAULT_ACOUSTICNESS: Final[float] = 0.50

# Mood classification thresholds based on valence/energy
VALENCE_HAPPY_THRESHOLD: Final[float] = 0.65
VALENCE_SAD_THRESHOLD: Final[float] = 0.35
ENERGY_INTENSE_THRESHOLD: Final[float] = 0.80

# CLI display constants
SEPARATOR_LINE: Final[str] = "=" * 70


def initialize_spotify_client() -> spotipy.Spotify:
    """Initialize and authenticate with Spotify API.
    
    DEV NOTE: Uses Client Credentials flow which is read-only and suitable
    for accessing public catalog data. Requires SPOTIPY_CLIENT_ID and
    SPOTIPY_CLIENT_SECRET environment variables.
    
    Returns:
        Authenticated Spotify client instance.
        
    Raises:
        SystemExit: If authentication fails due to missing credentials.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # DEV NOTE: SpotifyClientCredentials automatically reads
    # SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET from environment
    try:
        auth_manager = SpotifyClientCredentials()
        sp = spotipy.Spotify(auth_manager=auth_manager)
        return sp
    except Exception as e:
        print("❌ Error: Failed to authenticate with Spotify.", file=sys.stderr)
        print(f"   Ensure SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET are set.", file=sys.stderr)
        print(f"   Details: {e}", file=sys.stderr)
        sys.exit(1)


def extract_decade_from_date(release_date: str) -> str:
    """Extract decade string from Spotify release date.
    
    DEV NOTE: Spotify returns dates in various formats (YYYY, YYYY-MM, YYYY-MM-DD).
    This function extracts the decade (e.g., "2024" -> "2020") from the year portion.
    
    Args:
        release_date: Release date string from Spotify API.
        
    Returns:
        Decade string (e.g., "2020", "2010").
    """
    year = int(release_date[:4])
    decade = (year // 10) * 10
    return str(decade)


def calculate_mood(valence: float, energy: float) -> str:
    """Derive mood classification from Spotify audio features.
    
    DEV NOTE: Mood is inferred from valence (musical positivity) and energy.
    This is a simplified heuristic - real mood detection is more complex.
    
    Args:
        valence: Spotify valence score (0.0 = sad/negative, 1.0 = happy/positive).
        energy: Spotify energy score (0.0 = calm, 1.0 = energetic).
        
    Returns:
        Mood string classification.
    """
    if valence > VALENCE_HAPPY_THRESHOLD:
        return "happy"
    elif valence < VALENCE_SAD_THRESHOLD:
        return "sad"
    elif energy > ENERGY_INTENSE_THRESHOLD:
        return "intense"
    else:
        return "chill"


def fetch_audio_features(sp: spotipy.Spotify, track_id: str) -> dict[str, float | int]:
    """Fetch audio features from Spotify API with fallback handling.
    
    DEV NOTE: Spotify deprecated the Audio Features API in 2024. This function
    attempts to fetch real data but falls back to defaults on 403 errors.
    
    Args:
        sp: Authenticated Spotify client.
        track_id: Spotify track ID.
        
    Returns:
        Dictionary containing audio feature values.
    """
    try:
        features_list = sp.audio_features(track_id)
        
        if not features_list or not features_list[0]:
            raise ValueError("No audio features returned by Spotify.")
        
        features = features_list[0]
        
        return {
            "energy": round(features['energy'], 2),
            "danceability": round(features['danceability'], 2),
            "tempo_bpm": int(features['tempo']),
            "valence": round(features['valence'], 2),
            "acousticness": round(features['acousticness'], 2),
        }
    
    except Exception as e:
        print("\n❌ WARNING: Spotify Audio Features API unavailable (deprecated 2024)")
        print("❌ Falling back to default proxy values (0.50).")
        print("❌ Please manually update these values in the generated CSV!\n")
        
        return {
            "energy": DEFAULT_ENERGY,
            "danceability": DEFAULT_DANCEABILITY,
            "tempo_bpm": DEFAULT_TEMPO_BPM,
            "valence": DEFAULT_VALENCE,
            "acousticness": DEFAULT_ACOUSTICNESS,
        }


def format_csv_row(
    track_name: str,
    artist_name: str,
    mood: str,
    energy: float,
    tempo_bpm: int,
    valence: float,
    danceability: float,
    acousticness: float,
    popularity: int,
    decade: str,
) -> str:
    """Format song data as a CSV row.
    
    DEV NOTE: Uses [GENRE] as a placeholder because Spotify tracks genres by
    Artist, not by Song. The user must manually replace this with the appropriate
    genre (e.g., "dark pop", "indie rock"). Track and artist names are wrapped
    in quotes to handle potential commas.
    
    Args:
        track_name: Song title.
        artist_name: Artist name.
        mood: Derived mood classification.
        energy: Energy score (0.0-1.0).
        tempo_bpm: Tempo in beats per minute.
        valence: Valence score (0.0-1.0).
        danceability: Danceability score (0.0-1.0).
        acousticness: Acousticness score (0.0-1.0).
        popularity: Spotify popularity score (0-100).
        decade: Release decade string.
        
    Returns:
        Formatted CSV row string.
    """
    return (
        f'NEW_ID,"{track_name}","{artist_name}",[GENRE],{mood},'
        f'{energy},{tempo_bpm},{valence},{danceability},{acousticness},'
        f'{popularity},{decade}'
    )


def harvest_song_data(sp: spotipy.Spotify, search_query: str) -> None:
    """Search for a song and extract its data from Spotify.
    
    DEV NOTE: This is the main workflow function that orchestrates the search,
    metadata extraction, audio feature fetching, and CSV formatting.
    
    Args:
        sp: Authenticated Spotify client.
        search_query: Song name or search terms.
    """
    print(f"\n🔍 Searching Spotify for: '{search_query}'...")
    
    # Search for the track
    results = sp.search(q=search_query, type='track', limit=1)
    
    if not results['tracks']['items']:
        print("❌ No results found. Check your spelling!")
        return
    
    track = results['tracks']['items'][0]
    track_id = track['id']
    track_name = track['name']
    artist_name = track['artists'][0]['name']
    popularity = track['popularity']
    
    # Calculate decade from release date
    release_date = track['album']['release_date']
    decade = extract_decade_from_date(release_date)
    
    print(f"🎧 Found: {track_name} by {artist_name}")
    print("📊 Fetching audio features...")
    
    # Fetch audio features (with fallback)
    features = fetch_audio_features(sp, track_id)
    
    # Calculate mood from valence and energy
    mood = calculate_mood(features["valence"], features["energy"])
    
    # Display results
    print("\n✅ DATA HARVESTED SUCCESSFULLY!")
    print(SEPARATOR_LINE)
    print("Copy and paste this exact row into your data/songs.csv file:")
    print(SEPARATOR_LINE)
    
    csv_row = format_csv_row(
        track_name=track_name,
        artist_name=artist_name,
        mood=mood,
        energy=features["energy"],
        tempo_bpm=features["tempo_bpm"],
        valence=features["valence"],
        danceability=features["danceability"],
        acousticness=features["acousticness"],
        popularity=popularity,
        decade=decade,
    )
    
    print(csv_row)
    print(f"{SEPARATOR_LINE}\n")


def main() -> int:
    """Main entry point for the Spotify harvester CLI.
    
    Returns:
        Exit code (0 for success).
    """
    print("=== THE DARK VIBE MATRIX: SPOTIFY HARVESTER ===")
    
    # Initialize Spotify client
    sp = initialize_spotify_client()
    
    # Interactive CLI loop
    while True:
        try:
            query = input("Enter a song name to harvest (or type 'quit' to exit): ")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break
        
        query = query.strip()
        
        if query.lower() == 'quit':
            print("👋 Goodbye!")
            break
        
        if not query:
            print("⚠️ Please enter a valid search query.")
            continue
        
        harvest_song_data(sp, query)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
