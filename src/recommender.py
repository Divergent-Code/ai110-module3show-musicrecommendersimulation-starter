import csv

def load_songs(filepath):
    """Reads songs from a CSV file and converts numeric fields."""
    songs = []
    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row['energy'] = float(row['energy'])
            row['danceability'] = float(row['danceability'])
            row['popularity'] = int(row['popularity'])
            row['decade'] = int(row['decade'])
            songs.append(row)
    return songs

def score_song(user_prefs, song, mode="default"):
    """Calculates a relevance score using different strategic modes."""
    score = 0.0
    reasons = []

    # Pre-calculate our mathematical differences to keep code clean
    energy_diff = abs(song['energy'] - user_prefs['target_energy'])
    energy_score = max(0, 1.0 - energy_diff) 
    
    dance_diff = abs(song['danceability'] - user_prefs['target_danceability'])
    dance_score = max(0, 1.0 - dance_diff)

    # --- STRATEGY 1: Vibe Only (Ignore genre, mood, era, and pop) ---
    if mode == "vibe_only":
        score += energy_score + dance_score
        reasons.append(f"Energy (+{energy_score:.2f})")
        reasons.append(f"Dance (+{dance_score:.2f})")

    # --- STRATEGY 2: Genre Heavy (Massive filter bubble) ---
    elif mode == "genre_heavy":
        if song['genre'] == user_prefs['favorite_genre']:
            score += 3.0  # Massive priority to genre
            reasons.append("Genre match (+3.0)")
        if song['mood'] == user_prefs['favorite_mood']:
            score += 1.0
            reasons.append("Mood match (+1.0)")
        
        score += energy_score + dance_score
        reasons.append(f"Energy (+{energy_score:.2f})")
        reasons.append(f"Dance (+{dance_score:.2f})")

    # --- STRATEGY 3: Default (Balanced with all features) ---
    else: 
        if song['genre'] == user_prefs['favorite_genre']:
            score += 0.5
            reasons.append("Genre match (+0.5)")
        if song['mood'] == user_prefs['favorite_mood']:
            score += 1.0
            reasons.append("Mood match (+1.0)")
        
        pop_diff = abs(song['popularity'] - user_prefs['target_popularity'])
        pop_score = max(0, 1.0 - (pop_diff / 100))

        decade_diff = abs(song['decade'] - user_prefs['target_decade'])
        decade_score = 1.0 if decade_diff == 0 else (0.5 if decade_diff <= 10 else 0.0)
        
        score += energy_score + dance_score + pop_score + decade_score
        reasons.append(f"Energy (+{energy_score:.2f})")
        reasons.append(f"Dance (+{dance_score:.2f})")
        reasons.append(f"Pop (+{pop_score:.2f})")
        if decade_score > 0:
            reasons.append(f"Era (+{decade_score:.1f})")

    return round(score, 2), reasons

def recommend_songs(user_prefs, songs, k=5, mode="default"):
    """Scores all songs and returns the top k ranked recommendations."""
    scored_songs = []
    
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode)
        
        scored_songs.append({
            "song_data": song,
            "score": score,
            "reasons": reasons
        })

    ranked_songs = sorted(scored_songs, key=lambda x: x['score'], reverse=True)
    return ranked_songs[:k]