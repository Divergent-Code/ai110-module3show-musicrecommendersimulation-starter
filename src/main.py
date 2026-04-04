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

# Table format for tabulate output
TABLE_FORMAT: str = "fancy_grid"


def display_user_recommendations(user: UserProfile, mode: str, recommendations: list) -> None:
    """Format and display recommendations for a specific user and mode.
    
    DEV NOTE: Uses tabulate library for clean CLI table formatting.
    The fancy_grid format provides visual separation between sections.
    
    Args:
        user: User profile (used for display context).
        mode: Scoring mode name for header display.
        recommendations: List of recommendation results from recommend_songs().
    """
    print(f"--- Mode: {mode.upper()} ---")
    
    if not recommendations:
        print("No recommendations found.\n")
        return
    
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
    print(tabulate(table_data, headers=headers, tablefmt=TABLE_FORMAT))
    print()  # Blank line between modes


def display_user_header(user: UserProfile) -> None:
    """Display formatted header for a user section.
    
    Args:
        user: User profile containing name field.
    """
    user_name: str = user.get('name', 'User')  # type: ignore[typeddict-item]
    header_text = f"=== THE DARK VIBE MATRIX: SCORING MODES FOR {user_name.upper()} ==="
    separator = "=" * len(header_text)
    
    print(separator)
    print(header_text)
    print(f"{separator}\n")


def main() -> int:
    """Main entry point for the recommendation demo.
    
    DEV NOTE: Demonstrates the recommender engine by loading the song catalog
    and running multiple user profiles through different scoring modes.
    
    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Load song database
    try:
        songs = load_songs(SONGS_DATABASE_PATH)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Data error: {e}", file=sys.stderr)
        return 1
    
    print(f"Loaded {len(songs)} songs successfully!\n")
    
    # Process each demo user profile
    for current_user in DEMO_PROFILES:
        display_user_header(current_user)
        
        # Run each scoring mode for this user
        for mode in SCORING_MODES:
            recommendations = recommend_songs(
                current_user,
                songs,
                k=RECOMMENDATIONS_PER_MODE,
                mode=mode
            )
            display_user_recommendations(current_user, mode, recommendations)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
