"""
Music Recommender Demo Application.

This module provides a command-line demonstration of the music recommendation
engine, displaying results in formatted tables using different scoring strategies.

DEV NOTE: This is a demonstration script that creates sample user profiles
and runs them through the recommendation engine. In production, user profiles
would come from a database or user input interface.

Usage:
    python -m src.main
    python src/main.py
"""

import io
import sys
from pathlib import Path

# DEV NOTE: Force UTF-8 encoding for stdout on Windows to handle
# unicode characters in the fancy_grid table format.
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to PYTHONPATH for direct script execution
# DEV NOTE: This allows running the script directly (python src/main.py) without
# requiring the package to be installed. The insert at position 0 ensures our
# project takes precedence over any installed versions.
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from tabulate import tabulate
from src.recommender import load_songs, recommend_songs, UserProfile


# =============================================================================
# CONSTANTS
# =============================================================================
# DEV NOTE: These are demonstration user profiles representing different
# musical tastes. In a production system, these would be loaded from user data.

DEMO_PROFILES: list[UserProfile] = [
    {
        "name": "Rob",  # type: ignore[typeddict-item]
        "favorite_genre": "indie rock",
        "favorite_mood": "energetic",
        "target_energy": 0.80,
        "target_danceability": 0.60,
        "target_popularity": 45,
        "target_decade": 2000,
    },
    {
        "name": "Azalea",  # type: ignore[typeddict-item]
        "favorite_genre": "alt pop",
        "favorite_mood": "moody",
        "target_energy": 0.60,
        "target_danceability": 0.55,
        "target_popularity": 85,
        "target_decade": 2020,
    },
    {
        "name": "Onika",  # type: ignore[typeddict-item]
        "favorite_genre": "dark pop",
        "favorite_mood": "intense",
        "target_energy": 0.85,
        "target_danceability": 0.65,
        "target_popularity": 55,
        "target_decade": 2020,
    },
]

# Scoring modes to demonstrate different recommendation strategies
# DEV NOTE: Each mode represents a different algorithmic approach to illustrate
# how weighting affects recommendation diversity and filter bubble formation.
SCORING_MODES: list[str] = ["default", "vibe_only", "genre_heavy"]

# Data path relative to project root
SONGS_DATABASE_PATH: str = "data/songs.csv"

# Number of recommendations to display per mode
RECOMMENDATIONS_PER_MODE: int = 5


def display_recommendations(user: UserProfile, mode: str, recommendations: list) -> None:
    """Format and display recommendations in a table.
    
    DEV NOTE: Uses tabulate library for clean CLI table formatting.
    The fancy_grid format provides visual separation between modes.
    
    Args:
        user: User profile (used for display context).
        mode: Scoring mode name for header display.
        recommendations: List of recommendation results from recommend_songs().
    """
    print(f"--- Mode: {mode.upper()} ---")
    
    # Build table rows
    table_data: list[list] = []
    for rank, result in enumerate(recommendations, 1):
        song = result['song_data']
        
        # Join reasons with newlines for readability in table cells
        reasons_str = "\n".join(result['reasons'])
        
        table_data.append([
            rank,
            song['title'],
            song['artist'],
            result['score'],
            reasons_str,
        ])
    
    # Render table
    headers = ["Rank", "Song Title", "Artist", "Score", "Scoring Breakdown"]
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
    print()  # Blank line between modes


def main() -> int:
    """Main entry point for the recommendation demo.
    
    DEV NOTE: Demonstrates the recommender engine by loading the song catalog
    and running a selected user profile through multiple scoring modes.
    
    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Load song database
    try:
        songs = load_songs(SONGS_DATABASE_PATH)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except ValueError as e:
        print(f"Data error: {e}")
        return 1
    
    print(f"Loaded {len(songs)} songs successfully!\n")
    
    # Select demo user (Azalea profile shows clean penalized data)
    # DEV NOTE: Change index [0, 1, 2] to test different user profiles
    current_user = DEMO_PROFILES[1]
    user_name: str = current_user.get('name', 'User')  # type: ignore[typeddict-item]
    
    print(f"=== THE DARK VIBE MATRIX: SCORING MODES FOR {user_name.upper()} ===\n")
    
    # Run each scoring mode
    for mode in SCORING_MODES:
        recommendations = recommend_songs(
            current_user, 
            songs, 
            k=RECOMMENDATIONS_PER_MODE, 
            mode=mode
        )
        display_recommendations(current_user, mode, recommendations)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
