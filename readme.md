# Basic Spotify Playlist Extractor

A simple Python tool to extract all tracks from any Spotify playlist and export them to CSV or TXT files for analysis, backup, or sharing. I needed it because my wedding DJ wanted a physical list (not a spotify list) and I didn't want to write it out all myself :) 

## What This Tool Does

This application connects to [Spotify's Web API](https://developer.spotify.com/documentation/web-api) to fetch detailed information about every track in a playlist and saves the data in multiple formats:

- **CSV format**: Perfect for data analysis in Excel, Google Sheets, or Python/R
- **TXT format**: Human-readable format for easy viewing and sharing
- **Comprehensive data**: Extracts track names, artists, albums, release dates, popularity scores, and more

## What Data You Get

For each track, the tool extracts:

| Field | Description | Example |
|-------|-------------|---------|
| `track_name` | The name of the song | "Bohemian Rhapsody" |
| `artist_name` | Artist(s) who performed the track | "Queen" |
| `album_name` | Album the track appears on | "A Night at the Opera" |
| `release_date` | When the album was released | "1975-10-31" |
| `duration_ms` | Track length in milliseconds | 355000 |
| `duration_min_sec` | Human-readable track length | "5:55" |
| `popularity` | Spotify popularity score (0-100) | 87 |
| `spotify_url` | Direct link to the track on Spotify | "https://open.spotify.com/track/..." |
| `track_id` | Unique Spotify identifier | "4u7EnebtmKWzUH433cf5Qv" |
| `added_at` | When the track was added to playlist | "2023-12-01T15:30:00Z" |

### Understanding Popularity Scores
I thought this was a fun variable so wanted to give it a quick callout. Spotify's popularity score is calculated based on:
- Total number of plays
- How recent those plays are
- Ranges from 0 (least popular) to 100 (most popular)
- Updated in real-time, so scores can change
- More information on this can be found [here](https://developer.spotify.com/documentation/web-api/reference/get-an-artists-top-tracks). CTRL + F for 'popularity'.

## Prerequisites

- Python 3.7 or higher
- A Spotify account (free or premium)
- A Spotify Developer App (free to create)

## Setup Instructions

### Step 1: Get Your Spotify API Credentials

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click **"Create an App"**
4. Fill out the form:
   - **App name**: "Playlist Extractor" (or whatever you prefer)
   - **App description**: "Tool to extract playlist data"
   - **Redirect URI**: `http://localhost:8080` (required but not used)
   - Check the **Developer Terms of Service** box
5. Click **"Create"**
6. On your new app's page, click **"Settings"**
7. Copy your **Client ID** and **Client Secret** (keep these private!)

### Step 2: Clone and Setup the Project

```bash
# Clone or download this repository
git clone <your-repo-url>
cd spotify-playlist-extractor

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your actual values:
```env
# Required: Spotify API Credentials
SPOTIFY_CLIENT_ID=your_actual_client_id_here
SPOTIFY_CLIENT_SECRET=your_actual_client_secret_here
SPOTIFY_PLAYLIST_URL=https://open.spotify.com/playlist/your_playlist_id_here

# Optional: Output Configuration
OUTPUT_FORMAT=both
OUTPUT_DIRECTORY=./output
FILENAME_PREFIX=playlist
```

### Step 4: Get Your Playlist URL

1. Open Spotify (web, desktop, or mobile app)
2. Navigate to the playlist you want to extract
3. Click the **"Share"** button (three dots menu → Share)
4. Select **"Copy link to playlist"**
5. Paste this URL into your `.env` file as `SPOTIFY_PLAYLIST_URL`
_Note: Playlist must be public. By default, all playlists created are [public](https://support.spotify.com/uk/article/playlist-privacy-and-access/)._ 

Example playlist URLs:
- `https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M`
- `https://open.spotify.com/playlist/3cEYpjA9oz9GiPac4AsH4n?si=abc123`

## Usage

### Basic Usage

```bash
# Make sure your virtual environment is activated
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

# Run the extractor
python app.py
```

### Configuration Options

You can customize the output by modifying your `.env` file:

**Output Format Options:**
- `OUTPUT_FORMAT=csv` - Only create CSV file
- `OUTPUT_FORMAT=txt` - Only create TXT file  
- `OUTPUT_FORMAT=both` - Create both files (default)

**Output Directory:**
- `OUTPUT_DIRECTORY=./output` - Save to 'output' folder (default)
- `OUTPUT_DIRECTORY=./downloads` - Save to 'downloads' folder
- `OUTPUT_DIRECTORY=/Users/yourname/Music` - Save to specific path

**Filename Prefix:**
- `FILENAME_PREFIX=playlist` - Creates `playlist_123abc.csv` (default)
- `FILENAME_PREFIX=my_workout` - Creates `my_workout_123abc.csv`

### Sample Output

**CSV Output (will output in spreadsheet format):**
```csv
track_name,artist_name,album_name,release_date,duration_ms,duration_min_sec,popularity,spotify_url,track_id,added_at
"Bohemian Rhapsody","Queen","A Night at the Opera","1975-10-31",355000,"5:55",87,"https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv","4u7EnebtmKWzUH433cf5Qv","2023-12-01T15:30:00Z"
```

**TXT Output:**
```
SPOTIFY PLAYLIST TRACKS
==================================================

  1. Bohemian Rhapsody
     Artist: Queen
     Album: A Night at the Opera
     Duration: 5:55
     Release Date: 1975-10-31
     Spotify URL: https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv
```

## Troubleshooting

### Common Issues

**"Error: SPOTIFY_CLIENT_ID not found"**
- Make sure your `.env` file exists and contains your credentials
- Check that you're running the script from the correct directory

**"Error getting token: 400"**
- Verify your Client ID and Client Secret are correct
- Make sure there are no extra spaces in your `.env` file

**"Error fetching tracks: 401"**
- Your access token may have expired (tokens last 1 hour)
- Try running the script again - it will automatically get a new token

**"Error fetching tracks: 403"**
- The playlist might be private and require different authentication
- Make sure the playlist is public or you have access to it

### Getting Help

If you encounter issues:
1. Check that all required environment variables are set
2. Ensure your virtual environment is activated
3. Verify the playlist URL is correct and the playlist is accessible
4. Check the [Spotify Web API documentation](https://developer.spotify.com/documentation/web-api/) for API-related issues

## Technical Details

- Uses Spotify's **Client Credentials** authentication flow
- Works with public playlists (no user login required)
- Handles pagination automatically for large playlists
- Rate-limited and respectful of Spotify's API guidelines
- Exports comprehensive track metadata including popularity metrics

## File Structure

```
spotify-playlist-extractor/
├── app.py                 # Main application
├── .env                   # Your configuration (not in git)
├── .env.example          # Template for environment variables
├── .gitignore            # Git ignore rules
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── output/              # Generated files (created automatically)
    ├── playlist_123.csv
    └── playlist_123.txt
```

## Privacy and Security

- Your Spotify credentials are stored locally in `.env` and never shared
- The `.env` file is excluded from git to protect your secrets
- Only playlist metadata is accessed - no personal user data
- All API calls use HTTPS encryption

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is for educational and personal use. Please respect Spotify's Terms of Service and API usage guidelines.