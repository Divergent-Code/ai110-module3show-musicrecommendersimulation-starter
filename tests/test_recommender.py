"""
Unit tests for the Music Recommender Engine.

This module tests the core functionality of the recommendation system:
- Song scoring algorithms across different modes
- Recommendation ranking and diversity
- Edge cases and input validation

DEV NOTE: Tests use a minimal mock song dataset to ensure fast, deterministic
execution. Production datasets contain 45+ songs; tests use 2 songs for clarity.

Run with: pytest tests/test_recommender.py -v
"""

import pytest
from src.recommender import load_songs, score_song, recommend_songs, Song, UserProfile


# =============================================================================
# TEST FIXTURES
# =============================================================================
# DEV NOTE: Fixtures define consistent test data. Using functions rather than
# module-level constants allows test isolation and easier modification.

def make_test_song_pop() -> Song:
    """Create a test song matching pop/happy preferences.
    
    Returns:
        Song dict representing an upbeat pop track (Test Pop Track).
    """
    return {
        "id": "1",
        "title": "Test Pop Track",
        "artist": "Test Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "tempo_bpm": 120,
        "valence": 0.9,
        "danceability": 0.8,
        "acousticness": 0.2,
        "popularity": 80,
        "decade": 2020,
    }


def make_test_song_lofi() -> Song:
    """Create a test song matching lofi/chill preferences.
    
    Returns:
        Song dict representing a chill lofi track (Chill Lofi Loop).
    """
    return {
        "id": "2",
        "title": "Chill Lofi Loop",
        "artist": "Test Artist",  # Same artist as pop track (tests diversity)
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.4,
        "tempo_bpm": 80,
        "valence": 0.6,
        "danceability": 0.5,
        "acousticness": 0.9,
        "popularity": 45,
        "decade": 2010,
    }


def make_test_songs() -> list[Song]:
    """Create test song catalog with 2 tracks.
    
    DEV NOTE: Both songs share the same artist to test diversity penalty
    logic in recommend_songs().
    
    Returns:
        List containing pop and lofi test songs.
    """
    return [make_test_song_pop(), make_test_song_lofi()]


def make_test_user() -> UserProfile:
    """Create a test user profile matching the pop song.
    
    Returns:
        UserProfile dict targeting pop/happy/2020 preferences.
    """
    return {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "target_danceability": 0.8,
        "target_popularity": 80,
        "target_decade": 2020,
    }


# =============================================================================
# RECOMMENDATION ENGINE TESTS
# =============================================================================

def test_recommend_returns_songs_sorted_by_score() -> None:
    """Verify recommendations are ranked by score in descending order.
    
    DEV NOTE: Uses default mode which should rank pop song higher than lofi
    for a user preferring pop/happy vibes. Also verifies genre/mood matching.
    """
    user = make_test_user()
    songs = make_test_songs()
    
    results = recommend_songs(user, songs, k=2)
    
    # Verify we got exactly 2 recommendations
    assert len(results) == 2
    
    # First result should be the pop song (perfect match)
    assert results[0]['song_data']["genre"] == "pop"
    assert results[0]['song_data']["mood"] == "happy"
    
    # Results should be sorted by score (highest first)
    assert results[0]['score'] > results[1]['score']


def test_recommend_respects_k_parameter() -> None:
    """Verify k parameter limits the number of recommendations.
    
    DEV NOTE: Even with more songs available, should only return k items.
    """
    user = make_test_user()
    songs = make_test_songs()
    
    results = recommend_songs(user, songs, k=1)
    
    assert len(results) == 1


def test_recommend_with_empty_catalog() -> None:
    """Verify graceful handling of empty song catalog.
    
    DEV NOTE: Edge case - should return empty list, not crash.
    """
    user = make_test_user()
    results = recommend_songs(user, [], k=5)
    
    assert results == []


def test_recommend_k_equals_zero() -> None:
    """Verify k=0 returns empty list.
    
    DEV NOTE: Edge case for boundary conditions.
    """
    user = make_test_user()
    songs = make_test_songs()
    
    results = recommend_songs(user, songs, k=0)
    
    assert results == []


# =============================================================================
# SCORING ALGORITHM TESTS
# =============================================================================

def test_score_song_returns_score_and_reasons() -> None:
    """Verify score_song returns properly formatted output.
    
    DEV NOTE: Tests default mode which should include genre match reason.
    """
    user = make_test_user()
    song = make_test_song_pop()
    
    score, reasons = score_song(user, song)
    
    # Verify return types
    assert isinstance(score, float)
    assert isinstance(reasons, list)
    assert len(reasons) > 0
    
    # Should include genre match in default mode
    assert "Genre match (+0.5)" in reasons


def test_score_song_default_mode_structure() -> None:
    """Verify default mode includes all expected score components.
    
    DEV NOTE: Default mode should calculate scores for genre, mood, energy,
    danceability, popularity, and decade when applicable.
    """
    user = make_test_user()
    song = make_test_song_pop()  # Perfect match
    
    score, reasons = score_song(user, song, mode="default")
    
    # Should have high score for perfect match
    assert score > 3.0
    
    # Verify all expected reasons are present
    reason_text = " ".join(reasons)
    assert "Genre" in reason_text
    assert "Mood" in reason_text
    assert "Energy" in reason_text
    assert "Dance" in reason_text
    assert "Pop" in reason_text
    assert "Era" in reason_text


def test_score_song_vibe_only_mode() -> None:
    """Verify vibe_only mode ignores categorical features.
    
    DEV NOTE: vibe_only should only use energy and danceability,
    ignoring genre and mood matches entirely.
    """
    user = make_test_user()
    song = make_test_song_pop()
    
    score, reasons = score_song(user, song, mode="vibe_only")
    
    # Should NOT include genre match
    assert "Genre match" not in " ".join(reasons)
    
    # Should only have energy and dance reasons
    assert any("Energy" in r for r in reasons)
    assert any("Dance" in r for r in reasons)


def test_score_song_genre_heavy_mode() -> None:
    """Verify genre_heavy mode applies larger genre weight.
    
    DEV NOTE: genre_heavy applies +3.0 for genre match vs +0.5 in default,
    creating a stronger filter bubble effect.
    """
    user = make_test_user()
    song = make_test_song_pop()
    
    score, reasons = score_song(user, song, mode="genre_heavy")
    
    # Should have high genre bonus
    assert "Genre match (+3.0)" in reasons
    
    # Score should be higher than default mode due to larger genre weight
    default_score, _ = score_song(user, song, mode="default")
    assert score > default_score


def test_score_song_invalid_mode_raises() -> None:
    """Verify invalid mode raises ValueError.
    
    DEV NOTE: Error handling test for robustness.
    """
    user = make_test_user()
    song = make_test_song_pop()
    
    with pytest.raises(ValueError, match="Unknown scoring mode"):
        score_song(user, song, mode="invalid_mode")


# =============================================================================
# DATA LOADING TESTS
# =============================================================================

def test_load_songs_file_not_found() -> None:
    """Verify FileNotFoundError for missing database.
    
    DEV NOTE: Proper error handling allows calling code to handle missing data.
    """
    with pytest.raises(FileNotFoundError):
        load_songs("nonexistent/path/songs.csv")


def test_load_songs_invalid_data() -> None:
    """Verify ValueError for malformed CSV data.
    
    DEV NOTE: Tests that invalid numeric values are caught during loading
    rather than causing silent failures later.
    """
    import tempfile
    import os
    
    # Create a temp file with invalid data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness,popularity,decade\n")
        f.write("1,Test,Artist,pop,happy,invalid,120,0.5,0.5,0.5,80,2020\n")
        temp_path = f.name
    
    try:
        with pytest.raises(ValueError, match="Invalid data at row"):
            load_songs(temp_path)
    finally:
        os.unlink(temp_path)


# =============================================================================
# DIVERSITY PENALTY TESTS
# =============================================================================

def test_diversity_penalty_applied_to_same_artist() -> None:
    """Verify artist diversity penalty reduces scores for repeated artists.
    
    DEV NOTE: Both test songs have the same artist ("Test Artist").
    The second recommendation should have a diversity penalty applied.
    """
    user = make_test_user()
    songs = make_test_songs()
    
    results = recommend_songs(user, songs, k=2)
    
    # Second result should have diversity penalty in reasons
    second_reasons = " ".join(results[1]['reasons'])
    assert "Diversity Penalty" in second_reasons


def test_diversity_penalty_reduces_score() -> None:
    """Verify diversity penalty actually lowers the final score.
    
    DEV NOTE: By comparing base_score vs final score, we can verify
    the penalty is subtracted from same-artist subsequent picks.
    """
    user = make_test_user()
    songs = make_test_songs()
    
    # Score both songs individually to get base scores
    pop_score, _ = score_song(user, songs[0], mode="default")
    lofi_score, _ = score_song(user, songs[1], mode="default")
    
    # Get recommendations
    results = recommend_songs(user, songs, k=2, mode="default")
    
    # The lofi song should have a lower final score than its base score
    # due to diversity penalty (both have same artist)
    lofi_final_score = results[1]['score']
    assert lofi_final_score < lofi_score
