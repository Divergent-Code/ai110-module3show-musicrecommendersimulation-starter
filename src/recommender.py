"""
Music Recommender Engine - Content-Based Filtering Implementation.

This module implements a content-based music recommendation system that matches
user preferences against song features using configurable scoring strategies.

DEV NOTE: The scoring system uses normalized differences for numerical features
(energy, danceability, popularity) and exact matching for categorical features
(genre, mood). The decade feature uses tiered scoring to handle era preferences.

Architecture:
    - load_songs(): Data ingestion with type conversion and validation
    - score_song(): Feature-based scoring with multiple strategy modes
    - recommend_songs(): Greedy ranking with diversity penalty to avoid
      repetitive artist recommendations
"""

import csv
from pathlib import Path
from typing import TypedDict


# =============================================================================
# CONSTANTS - Scoring weights and penalties
# =============================================================================
# DEV NOTE: These weights control the "filter bubble" effect. Higher genre
# weights create stronger bubbles by prioritizing genre matches over
# audio feature similarity.

# Default mode weights (balanced approach)
WEIGHT_GENRE_DEFAULT: float = 0.5
WEIGHT_MOOD_DEFAULT: float = 1.0

# Genre-heavy mode weights (creates filter bubble effect)
WEIGHT_GENRE_HEAVY: float = 3.0
WEIGHT_MOOD_HEAVY: float = 1.0

# Diversity penalty applied to repeated artists
DIVERSITY_PENALTY: float = 1.5

# Decade matching thresholds (years)
DECADE_EXACT_MATCH: int = 0
DECADE_CLOSE_MATCH: int = 10

# Score thresholds
SCORE_DECADE_EXACT: float = 1.0
SCORE_DECADE_CLOSE: float = 0.5
SCORE_DECADE_NONE: float = 0.0

# Normalization factor for popularity (0-100 scale)
POPULARITY_MAX: int = 100


# =============================================================================
# TYPE DEFINITIONS
# =============================================================================
# DEV NOTE: Using TypedDict for clear data contracts without overhead
# of full dataclasses. These represent the CSV schema and user profile structure.

class Song(TypedDict):
    """Schema for song data loaded from CSV.
    
    DEV NOTE: All numeric fields are converted from strings during load_songs().
    The tempo_bpm, valence, and acousticness fields are present in the dataset
    but not currently used in scoring algorithms.
    """
    id: str
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: int
    valence: float
    danceability: float
    acousticness: float
    popularity: int
    decade: int


class UserProfile(TypedDict):
    """Schema for user preference profile.
    
    DEV NOTE: target_energy and target_danceability use 0.0-1.0 scale to
    match the Spotify audio features standard used in the dataset.
    target_popularity uses 0-100 scale (Spotify's popularity metric).
    target_decade is the preferred release decade (e.g., 2020, 2000).
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_danceability: float
    target_popularity: int
    target_decade: int


class ScoredSong(TypedDict):
    """Internal representation of a song with computed scores.
    
    DEV NOTE: current_score and current_reasons are mutable during the
    greedy selection process in recommend_songs() to apply diversity penalties.
    """
    song_data: Song
    base_score: float
    current_score: float
    reasons: list[str]
    current_reasons: list[str]


class RecommendationResult(TypedDict):
    """Final output format for recommendations."""
    song_data: Song
    score: float
    reasons: list[str]


# =============================================================================
# DATA LOADING
# =============================================================================

def load_songs(filepath: str | Path) -> list[Song]:
    """Load and parse song data from CSV file.
    
    DEV NOTE: This function handles type conversion from CSV strings to
    appropriate Python types. Missing files or malformed rows will raise
    exceptions - caller should handle FileNotFoundError.
    
    Args:
        filepath: Path to CSV file containing song data.
        
    Returns:
        List of Song dictionaries with typed fields.
        
    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If numeric conversion fails for any field.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Song database not found: {path.absolute()}")
    
    songs: list[Song] = []
    
    # DEV NOTE: Using utf-8-sig to handle BOM if present (common in Windows CSV exports)
    with open(path, mode='r', encoding='utf-8-sig', newline='') as file:
        reader = csv.DictReader(file)
        
        for row_num, row in enumerate(reader, start=2):  # start=2 for human-friendly line numbers
            try:
                song: Song = {
                    'id': row['id'],
                    'title': row['title'],
                    'artist': row['artist'],
                    'genre': row['genre'],
                    'mood': row['mood'],
                    'energy': float(row['energy']),
                    'tempo_bpm': int(row['tempo_bpm']),
                    'valence': float(row['valence']),
                    'danceability': float(row['danceability']),
                    'acousticness': float(row['acousticness']),
                    'popularity': int(row['popularity']),
                    'decade': int(row['decade']),
                }
                songs.append(song)
            except (KeyError, ValueError) as e:
                # DEV NOTE: Skip malformed rows instead of crashing entire load
                raise ValueError(f"Invalid data at row {row_num}: {e}")
    
    return songs


# =============================================================================
# SCORING LOGIC
# =============================================================================

def _calculate_numerical_scores(
    user_prefs: UserProfile,
    song: Song
) -> tuple[float, float, float, float]:
    """Calculate similarity scores for numerical features.
    
    DEV NOTE: All scores use 1.0 - normalized_difference to convert
    distance metrics into similarity scores (higher = better match).
    
    Args:
        user_prefs: User preference profile.
        song: Song data to score.
        
    Returns:
        Tuple of (energy_score, dance_score, pop_score, decade_score).
    """
    # Energy: direct difference on 0.0-1.0 scale
    energy_diff = abs(song['energy'] - user_prefs['target_energy'])
    energy_score = max(0.0, 1.0 - energy_diff)
    
    # Danceability: direct difference on 0.0-1.0 scale
    dance_diff = abs(song['danceability'] - user_prefs['target_danceability'])
    dance_score = max(0.0, 1.0 - dance_diff)
    
    # Popularity: normalized difference on 0-100 scale
    pop_diff = abs(song['popularity'] - user_prefs['target_popularity'])
    pop_score = max(0.0, 1.0 - (pop_diff / POPULARITY_MAX))
    
    # Decade: tiered scoring (exact = 1.0, within 10 years = 0.5, else 0.0)
    decade_diff = abs(song['decade'] - user_prefs['target_decade'])
    if decade_diff == DECADE_EXACT_MATCH:
        decade_score = SCORE_DECADE_EXACT
    elif decade_diff <= DECADE_CLOSE_MATCH:
        decade_score = SCORE_DECADE_CLOSE
    else:
        decade_score = SCORE_DECADE_NONE
    
    return energy_score, dance_score, pop_score, decade_score


def score_song(
    user_prefs: UserProfile,
    song: Song,
    mode: str = "default"
) -> tuple[float, list[str]]:
    """Calculate relevance score for a song based on user preferences.
    
    DEV NOTE: Three scoring modes available:
    - "default": Balanced scoring with all features (max ~4.0 points)
    - "vibe_only": Audio features only, ignores genre/mood/era (max 2.0 points)
    - "genre_heavy": Prioritizes genre match, creates filter bubble (max ~5.0 points)
    
    Args:
        user_prefs: User preference profile.
        song: Song to evaluate.
        mode: Scoring strategy - "default", "vibe_only", or "genre_heavy".
        
    Returns:
        Tuple of (total_score, list_of_reasons).
        
    Raises:
        ValueError: If an unknown mode is specified.
    """
    score = 0.0
    reasons: list[str] = []
    
    # Pre-calculate numerical feature scores
    energy_score, dance_score, pop_score, decade_score = _calculate_numerical_scores(
        user_prefs, song
    )
    
    # Strategy 1: Vibe Only - Focus on audio features, ignore categorical data
    if mode == "vibe_only":
        score += energy_score + dance_score
        reasons.append(f"Energy (+{energy_score:.2f})")
        reasons.append(f"Dance (+{dance_score:.2f})")
    
    # Strategy 2: Genre Heavy - Massive genre bias creates filter bubble
    elif mode == "genre_heavy":
        if song['genre'] == user_prefs['favorite_genre']:
            score += WEIGHT_GENRE_HEAVY
            reasons.append(f"Genre match (+{WEIGHT_GENRE_HEAVY:.1f})")
        if song['mood'] == user_prefs['favorite_mood']:
            score += WEIGHT_MOOD_HEAVY
            reasons.append(f"Mood match (+{WEIGHT_MOOD_HEAVY:.1f})")
        
        score += energy_score + dance_score
        reasons.append(f"Energy (+{energy_score:.2f})")
        reasons.append(f"Dance (+{dance_score:.2f})")
    
    # Strategy 3: Default - Balanced weighting across all features
    elif mode == "default":
        if song['genre'] == user_prefs['favorite_genre']:
            score += WEIGHT_GENRE_DEFAULT
            reasons.append(f"Genre match (+{WEIGHT_GENRE_DEFAULT:.1f})")
        if song['mood'] == user_prefs['favorite_mood']:
            score += WEIGHT_MOOD_DEFAULT
            reasons.append(f"Mood match (+{WEIGHT_MOOD_DEFAULT:.1f})")
        
        score += energy_score + dance_score + pop_score + decade_score
        reasons.append(f"Energy (+{energy_score:.2f})")
        reasons.append(f"Dance (+{dance_score:.2f})")
        reasons.append(f"Pop (+{pop_score:.2f})")
        if decade_score > 0:
            reasons.append(f"Era (+{decade_score:.1f})")
    
    else:
        raise ValueError(f"Unknown scoring mode: {mode}. Use 'default', 'vibe_only', or 'genre_heavy'.")
    
    return round(score, 2), reasons


# =============================================================================
# RECOMMENDATION ENGINE
# =============================================================================

def recommend_songs(
    user_prefs: UserProfile,
    songs: list[Song],
    k: int = 5,
    mode: str = "default"
) -> list[RecommendationResult]:
    """Generate top-k song recommendations with diversity enforcement.
    
    DEV NOTE: Uses greedy iterative selection with artist diversity penalty.
    After each selection, remaining songs by the same artist are penalized
    to ensure variety in recommendations. This is O(k*n) complexity.
    
    Algorithm:
        1. Score all songs using specified mode
        2. Iteratively select highest-scoring song
        3. Apply diversity penalty to same-artist songs
        4. Repeat until k songs selected or pool exhausted
    
    Args:
        user_prefs: User preference profile.
        songs: Complete song catalog to search.
        k: Number of recommendations to return.
        mode: Scoring strategy passed to score_song().
        
    Returns:
        List of k recommendation results, sorted by final score (descending).
    """
    if k <= 0:
        return []
    
    # Step 1: Calculate base scores for entire catalog
    pool: list[ScoredSong] = []
    for song in songs:
        base_score, reasons = score_song(user_prefs, song, mode)
        pool.append({
            "song_data": song,
            "base_score": base_score,
            "current_score": base_score,
            "reasons": reasons,
            "current_reasons": reasons.copy(),
        })
    
    final_recommendations: list[RecommendationResult] = []
    seen_artists: set[str] = set()
    
    # Step 2: Greedy selection with diversity penalty
    while len(final_recommendations) < k and pool:
        
        # Apply diversity penalty to artists already in recommendations
        for item in pool:
            item['current_score'] = item['base_score']
            item['current_reasons'] = item['reasons'].copy()
            
            # DEV NOTE: Diversity penalty reduces score but doesn't eliminate,
            # allowing same-artist songs to still rank highly if they're
            # significantly better matches than alternatives
            if item['song_data']['artist'] in seen_artists:
                item['current_score'] -= DIVERSITY_PENALTY
                
                # Avoid duplicate penalty annotations
                penalty_note = f"Diversity Penalty (-{DIVERSITY_PENALTY:.1f})"
                if penalty_note not in item['current_reasons']:
                    item['current_reasons'].append(penalty_note)
        
        # Sort by adjusted scores (descending) and select best
        pool.sort(key=lambda x: x['current_score'], reverse=True)
        best_match = pool.pop(0)
        
        # Record recommendation
        final_recommendations.append({
            "song_data": best_match['song_data'],
            "score": round(best_match['current_score'], 2),
            "reasons": best_match['current_reasons'],
        })
        seen_artists.add(best_match['song_data']['artist'])
    
    return final_recommendations
