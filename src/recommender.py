import csv

def load_songs(filepath):
    """Reads songs from a CSV file and converts numeric fields."""
    songs = []
    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row['energy'] = float(row['energy'])
            row['danceability'] = float(row['danceability'])
            # Convert our new columns to integers!
            row['popularity'] = int(row['popularity'])
            row['decade'] = int(row['decade'])
            songs.append(row)
    return songs

def score_song(user_prefs, song):
    """Calculates a relevance score out of 7.5 now!"""
    score = 0.0
    reasons = []

    # 1. Genre Match (+0.5 points from our Phase 4 experiment)
    if song['genre'] == user_prefs['favorite_genre']:
        score += 0.5
        reasons.append("Genre match (+0.5)")

    # 2. Mood Match (+1.0 point)
    if song['mood'] == user_prefs['favorite_mood']:
        score += 1.0
        reasons.append("Mood match (+1.0)")

    # 3. Energy Match (Up to +1.0 point)
    energy_diff = abs(song['energy'] - user_prefs['target_energy'])
    energy_score = max(0, 1.0 - energy_diff) 
    score += energy_score
    reasons.append(f"Energy (+{energy_score:.2f})")

    # 4. Danceability Match (Up to +1.0 point)
    dance_diff = abs(song['danceability'] - user_prefs['target_danceability'])
    dance_score = max(0, 1.0 - dance_diff)
    score += dance_score
    reasons.append(f"Dance (+{dance_score:.2f})")

    # 5. NEW: Popularity Match (Up to +1.0 point)
    # Calculate percentage difference out of 100
    pop_diff = abs(song['popularity'] - user_prefs['target_popularity'])
    pop_score = max(0, 1.0 - (pop_diff / 100))
    score += pop_score
    reasons.append(f"Pop (+{pop_score:.2f})")

    # 6. NEW: Decade Match (Up to +1.0 point)
    # Give 1.0 for exact decade, 0.5 for 10 years off, 0 for anything further
    decade_diff = abs(song['decade'] - user_prefs['target_decade'])
    if decade_diff == 0:
        decade_score = 1.0
    elif decade_diff <= 10:
        decade_score = 0.5
    else:
        decade_score = 0.0
    
    if decade_score > 0:
        score += decade_score
        reasons.append(f"Era (+{decade_score:.1f})")

    return round(score, 2), reasons


def recommend_songs(user_prefs, songs, k=5):
    """Scores all songs and returns the top k ranked recommendations."""
    scored_songs = []
    
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        
        scored_songs.append({
            "song_data": song,
            "score": score,
            "reasons": reasons
        })

    ranked_songs = sorted(scored_songs, key=lambda x: x['score'], reverse=True)
    return ranked_songs[:k]