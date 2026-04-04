from recommender import load_songs, recommend_songs

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
            "target_danceability": 0.60
        },
        {
            "name": "Azalea",
            "favorite_genre": "alt pop",
            "favorite_mood": "moody",
            "target_energy": 0.60,
            "target_danceability": 0.55
        },
        {
            "name": "Onika",
            "favorite_genre": "dark pop",
            "favorite_mood": "intense",
            "target_energy": 0.85,
            "target_danceability": 0.65
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