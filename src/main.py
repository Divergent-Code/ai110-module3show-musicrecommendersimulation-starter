import sys
from pathlib import Path
from tabulate import tabulate

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
            "target_popularity": 45,  
            "target_decade": 2000     
        },
        {
            "name": "Azalea",
            "favorite_genre": "alt pop",
            "favorite_mood": "moody",
            "target_energy": 0.60,
            "target_danceability": 0.55,
            "target_popularity": 85,  
            "target_decade": 2020     
        },
        {
            "name": "Onika",
            "favorite_genre": "dark pop",
            "favorite_mood": "intense",
            "target_energy": 0.85,
            "target_danceability": 0.65,
            "target_popularity": 55,  
            "target_decade": 2020     
        }
    ]

    # Let's keep using Azalea's profile to see the clean, penalized data!
    current_user = profiles[1]
    
    scoring_modes = ["default", "vibe_only", "genre_heavy"]

    print(f"=== THE DARK VIBE MATRIX: SCORING MODES FOR {current_user['name'].upper()} ===\n")

    # Loop through the modes
    for mode in scoring_modes:
        print(f"--- Mode: {mode.upper()} ---")
        top_songs = recommend_songs(current_user, songs, k=5, mode=mode) 
        
        # Prepare the data for our visual table
        table_data = []
        for i, result in enumerate(top_songs, 1):
            song = result['song_data']
            
            # Join the reasons with a newline so the table column doesn't get too wide
            reasons_str = "\n".join(result['reasons']) 
            
            table_data.append([
                i, 
                song['title'], 
                song['artist'], 
                result['score'], 
                reasons_str
            ])
            
        # Draw the table! We are using the "fancy_grid" format for a super clean look.
        headers = ["Rank", "Song Title", "Artist", "Score", "Scoring Breakdown"]
        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
        print("\n")

if __name__ == "__main__":
    main()