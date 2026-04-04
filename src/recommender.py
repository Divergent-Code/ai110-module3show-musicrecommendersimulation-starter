import csv

def load_songs(filepath):
    """Reads songs from a CSV file and converts numeric fields to floats."""
    songs = []
    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row['energy'] = float(row['energy'])
            row['danceability'] = float(row['danceability'])
            songs.append(row)
    return songs

def score_song(user_prefs, song):
    """Calculates a relevance score out of 5.0 and returns reasons."""
    score = 0.0
    reasons = []

    # 1. Genre Match (+2.0 points)
    if song['genre'] == user_prefs['favorite_genre']:
        score += 2.0
        reasons.append("Genre match (+2.0)")

    # 2. Mood Match (+1.0 point)
    if song['mood'] == user_prefs['favorite_mood']:
        score += 1.0
        reasons.append("Mood match (+1.0)")

    # 3. Energy Match (Up to +1.0 point)
    energy_diff = abs(song['energy'] - user_prefs['target_energy'])
    energy_score = max(0, 1.0 - energy_diff) 
    score += energy_score
    reasons.append(f"Energy match (+{energy_score:.2f})")

    # 4. Danceability Match (Up to +1.0 point)
    dance_diff = abs(song['danceability'] - user_prefs['target_danceability'])
    dance_score = max(0, 1.0 - dance_diff)
    score += dance_score
    reasons.append(f"Dance match (+{dance_score:.2f})")

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