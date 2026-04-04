import sys
from pathlib import Path

# Add project root to PYTHONPATH so it can be run directly via IDE or python src/main.py
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.recommender import load_songs, recommend_songs

def main():
    # 1. Load the database
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs successfully!\n")

    # 2. Define our diverse test profiles
    profiles = [
        {
            "name": "Rob",
            "favorite_genre": "indie rock",
            "favorite_mood": "energetic",
            "target_energy": 0.80,
            "target_danceability": 0.60,
            "target_popularity": 45,  # Underground/Indie
            "target_decade": 2000     # 2000s Nostalgia
        },
        {
            "name": "Azalea",
            "favorite_genre": "alt pop",
            "favorite_mood": "moody",
            "target_energy": 0.60,
            "target_danceability": 0.55,
            "target_popularity": 85,  # Mainstream hits
            "target_decade": 2020     # Modern music
        },
        {
            "name": "Onika",
            "favorite_genre": "dark pop",
            "favorite_mood": "intense",
            "target_energy": 0.85,
            "target_danceability": 0.65,
            "target_popularity": 55,  # Obscure/Underground
            "target_decade": 2020     # Modern edge
        }
    ]

    # 3. Loop through each profile, calculate scores, and print the ranking
    for user in profiles:
        print(f"--- Top 5 Recommendations for {user['name']} ---")
        top_songs = recommend_songs(user, songs, k=5)
        
        for i, result in enumerate(top_songs, 1):
            song = result['song_data']
            score = result['score']
            reasons = ", ".join(result['reasons'])
            
            print(f"{i}. {song['title']} by {song['artist']} (Score: {score})")
            print(f"   Why: {reasons}")
        print("\n")

if __name__ == "__main__":
    main()