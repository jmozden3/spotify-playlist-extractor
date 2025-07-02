import requests
import csv
import base64
import json
import os
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SpotifyPlaylistExtractor:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        
    def get_access_token(self):
        """Get access token using Client Credentials flow"""
        # Encode credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        # Request token
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials'
        }
        
        response = requests.post('https://accounts.spotify.com/api/token', 
                               headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            return True
        else:
            print(f"Error getting token: {response.status_code}")
            print(response.text)
            return False
    
    def extract_playlist_id(self, playlist_url):
        """Extract playlist ID from Spotify URL"""
        # Handle different URL formats
        if 'spotify.com' in playlist_url:
            # Extract from web URL like: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
            parsed = urlparse(playlist_url)
            playlist_id = parsed.path.split('/')[-1]
            # Remove query parameters if present
            playlist_id = playlist_id.split('?')[0]
            return playlist_id
        elif 'spotify:playlist:' in playlist_url:
            # Extract from URI like: spotify:playlist:37i9dQZF1DXcBWIGoYBM5M
            return playlist_url.split(':')[-1]
        else:
            # Assume it's already just the ID
            return playlist_url
    
    def get_playlist_tracks(self, playlist_id):
        """Get all tracks from a playlist"""
        if not self.access_token:
            if not self.get_access_token():
                return None
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        tracks = []
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        
        while url:
            # Parameters to get specific fields and handle pagination
            params = {
                'limit': 50,  # Max items per request
                'fields': 'items(added_at,track(id,name,artists(name),album(name,release_date),duration_ms,popularity,external_urls)),next'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data['items']:
                    track = item['track']
                    if track:  # Some tracks might be None (removed/unavailable)
                        track_info = {
                            'track_name': track.get('name', 'N/A'),
                            'artist_name': ', '.join([artist['name'] for artist in track.get('artists', [])]),
                            'album_name': track.get('album', {}).get('name', 'N/A'),
                            'release_date': track.get('album', {}).get('release_date', 'N/A'),
                            'duration_ms': track.get('duration_ms', 0),
                            'duration_min_sec': self.ms_to_min_sec(track.get('duration_ms', 0)),
                            'popularity': track.get('popularity', 0),
                            'spotify_url': track.get('external_urls', {}).get('spotify', 'N/A'),
                            'track_id': track.get('id', 'N/A'),
                            'added_at': item.get('added_at', 'N/A')
                        }
                        tracks.append(track_info)
                
                # Check if there are more pages
                url = data.get('next')
            else:
                print(f"Error fetching tracks: {response.status_code}")
                print(response.text)
                break
        
        return tracks
    
    def ms_to_min_sec(self, milliseconds):
        """Convert milliseconds to MM:SS format"""
        if not milliseconds:
            return "0:00"
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def save_to_csv(self, tracks, filename):
        """Save tracks to CSV file"""
        if not tracks:
            print("No tracks to save")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['track_name', 'artist_name', 'album_name', 'release_date', 
                         'duration_ms', 'duration_min_sec', 'popularity', 'spotify_url', 'track_id', 'added_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for track in tracks:
                writer.writerow(track)
        
        print(f"Successfully saved {len(tracks)} tracks to {filename}")
    
    def save_to_txt(self, tracks, filename):
        """Save tracks to TXT file in a readable format"""
        if not tracks:
            print("No tracks to save")
            return
            
        with open(filename, 'w', encoding='utf-8') as txtfile:
            txtfile.write("SPOTIFY PLAYLIST TRACKS\n")
            txtfile.write("=" * 50 + "\n\n")
            
            for i, track in enumerate(tracks, 1):
                txtfile.write(f"{i:3d}. {track['track_name']}\n")
                txtfile.write(f"     Artist: {track['artist_name']}\n")
                txtfile.write(f"     Album: {track['album_name']}\n")
                txtfile.write(f"     Duration: {track['duration_min_sec']}\n")
                txtfile.write(f"     Release Date: {track['release_date']}\n")
                txtfile.write(f"     Spotify URL: {track['spotify_url']}\n")
                txtfile.write("\n")
        
        print(f"Successfully saved {len(tracks)} tracks to {filename}")

def main():
    # Load credentials and configuration from environment variables
    CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    PLAYLIST_URL = os.getenv('SPOTIFY_PLAYLIST_URL')
    
    # Optional configuration with defaults
    OUTPUT_FORMAT = os.getenv('OUTPUT_FORMAT', 'both').lower()  # 'csv', 'txt', or 'both'
    OUTPUT_DIRECTORY = os.getenv('OUTPUT_DIRECTORY', './output')
    FILENAME_PREFIX = os.getenv('FILENAME_PREFIX', 'playlist')
    
    # Validate that required environment variables are set
    if not CLIENT_ID:
        print("Error: SPOTIFY_CLIENT_ID not found in environment variables")
        return
    if not CLIENT_SECRET:
        print("Error: SPOTIFY_CLIENT_SECRET not found in environment variables")
        return
    if not PLAYLIST_URL:
        print("Error: SPOTIFY_PLAYLIST_URL not found in environment variables")
        return
    
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
        print(f"Created output directory: {OUTPUT_DIRECTORY}")
    
    # Initialize extractor
    extractor = SpotifyPlaylistExtractor(CLIENT_ID, CLIENT_SECRET)
    
    # Extract playlist ID from URL
    playlist_id = extractor.extract_playlist_id(PLAYLIST_URL)
    print(f"Extracting tracks from playlist ID: {playlist_id}")
    
    # Get tracks
    tracks = extractor.get_playlist_tracks(playlist_id)
    
    if tracks:
        print(f"Found {len(tracks)} tracks")
        
        # Generate file paths
        csv_filename = os.path.join(OUTPUT_DIRECTORY, f'{FILENAME_PREFIX}_{playlist_id}.csv')
        txt_filename = os.path.join(OUTPUT_DIRECTORY, f'{FILENAME_PREFIX}_{playlist_id}.txt')
        
        # Save based on OUTPUT_FORMAT setting
        if OUTPUT_FORMAT in ['csv', 'both']:
            extractor.save_to_csv(tracks, csv_filename)
        if OUTPUT_FORMAT in ['txt', 'both']:
            extractor.save_to_txt(tracks, txt_filename)
        if OUTPUT_FORMAT not in ['csv', 'txt', 'both']:
            print(f"Invalid OUTPUT_FORMAT: {OUTPUT_FORMAT}. Using 'both' as default.")
            extractor.save_to_csv(tracks, csv_filename)
            extractor.save_to_txt(tracks, txt_filename)
    else:
        print("No tracks found or error occurred")

if __name__ == "__main__":
    main()