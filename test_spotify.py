import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def test_spotify_connection():
    # Load environment variables
    load_dotenv()
    
    # Print environment variables (without secrets)
    print("Checking environment variables...")
    print(f"SPOTIFY_CLIENT_ID exists: {'SPOTIFY_CLIENT_ID' in os.environ}")
    print(f"SPOTIFY_CLIENT_SECRET exists: {'SPOTIFY_CLIENT_SECRET' in os.environ}")
    print(f"SPOTIFY_REDIRECT_URI exists: {'SPOTIFY_REDIRECT_URI' in os.environ}")
    
    try:
        print("\nTrying to connect to Spotify...")
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
            redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
            scope="user-read-currently-playing"
        ))
        
        print("\nTrying to get current track...")
        current_track = sp.current_user_playing_track()
        
        if current_track is not None and current_track.get('item'):
            track = current_track['item']
            print("\nCurrently playing:")
            print(f"Track: {track['name']}")
            print(f"Artist: {track['artists'][0]['name']}")
            print(f"Album: {track['album']['name']}")
        else:
            print("\nNo track currently playing")
            
        print("\nSpotify connection test successful!")
        return True
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return False

if __name__ == "__main__":
    test_spotify_connection()
