from src.recommender import score_song, recommend_songs

def make_small_songs_list():
    return [
        {
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
            "decade": 2020
        },
        {
            "id": "2",
            "title": "Chill Lofi Loop",
            "artist": "Test Artist",
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.4,
            "tempo_bpm": 80,
            "valence": 0.6,
            "danceability": 0.5,
            "acousticness": 0.9,
            "popularity": 45,
            "decade": 2010
        },
    ]

def test_recommend_returns_songs_sorted_by_score():
    user = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "target_danceability": 0.8,
        "target_popularity": 80,
        "target_decade": 2020
    }
    songs = make_small_songs_list()
    results = recommend_songs(user, songs, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0]['song_data']["genre"] == "pop"
    assert results[0]['song_data']["mood"] == "happy"
    assert results[0]['score'] > results[1]['score']

def test_score_song_returns_score_and_reasons():
    user = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "target_danceability": 0.8,
        "target_popularity": 80,
        "target_decade": 2020
    }
    song = make_small_songs_list()[0]

    score, reasons = score_song(user, song)
    assert isinstance(score, float)
    assert isinstance(reasons, list)
    assert len(reasons) > 0
    assert "Genre match (+0.5)" in reasons
