import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# 1. Load your secret keys from the .env file
load_dotenv()

# 2. Authenticate with Spotify (Client Credentials Flow)
# This grants us read-only access to Spotify's entire public catalog!
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

def harvest_song_data(search_query):
    print(f"\n🔍 Searching Spotify mainframe for: '{search_query}'...")
    
    # Search for the track
    results = sp.search(q=search_query, type='track', limit=1)
    
    if not results['tracks']['items']:
        print("❌ No results found. Check your spelling!")
        return
        
    track = results['tracks']['items'][0]
    track_id = track['id']
    track_name = track['name']
    artist_name = track['artists'][0]['name']
    popularity = track['popularity']
    
    # Calculate the decade from the release date (e.g. 2024 -> 2020)
    release_date = track['album']['release_date']
    decade = release_date[:3] + "0" 
    
    print(f"🎧 Found: {track_name} by {artist_name}")
    print("📊 Fetching proprietary audio features...")
    
    # Get Spotify's secret audio math for this specific track
    try:
        features_list = sp.audio_features(track_id)
        if not features_list or not features_list[0]:
            raise ValueError("No audio features returned by Spotify.")
            
        features = features_list[0]
        
        energy = round(features['energy'], 2)
        danceability = round(features['danceability'], 2)
        tempo_bpm = int(features['tempo'])
        valence = round(features['valence'], 2)
        acousticness = round(features['acousticness'], 2)
    except Exception as e:
        print("\n❌ WARNING: Spotify has deprecated their Audio Features API! (HTTP 403)")
        print("❌ We can still fetch the Title, Artist, and Popularity, but the audio math is locked.")
        print("❌ Substituting default proxy values (0.50). You can manually edit these in the CSV!")
        
        # Fallback proxy values to prevent the script from breaking
        energy = 0.50
        danceability = 0.50
        tempo_bpm = 120
        valence = 0.50
        acousticness = 0.50
    
    # Auto-calculate a mood based on Spotify's "valence" (positivity) metric
    if valence > 0.65:
        mood = "happy"
    elif valence < 0.35:
        mood = "sad"
    elif energy > 0.8:
        mood = "intense"
    else:
        mood = "chill"
        
    print("\n✅ DATA HARVESTED SUCCESSFULLY!")
    print("=" * 70)
    print("Copy and paste this exact row into your data/songs.csv file:")
    print("=" * 70)
    
    # Note: We put [GENRE] as a placeholder because Spotify tracks genres by Artist, not by Song!
    # You will manually swap [GENRE] for "dark pop", "indie rock", etc.
    # We wrap track and artist names in quotes just in case they contain commas!
    csv_row = f'NEW_ID,"{track_name}","{artist_name}",[GENRE],{mood},{energy},{tempo_bpm},{valence},{danceability},{acousticness},{popularity},{decade}'
    
    print(csv_row)
    print("=" * 70 + "\n")

if __name__ == "__main__":
    print("=== THE DARK VIBE MATRIX: SPOTIFY HARVESTER ===")
    while True:
        query = input("Enter a song name to harvest (or type 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        harvest_song_data(query)