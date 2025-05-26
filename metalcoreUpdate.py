import praw
import spotipy
import os
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth
from dotenv   import load_dotenv
from datetime import datetime, timedelta
import json

class ConnectSpotify():

    def __init__(self):

        SPOTIFY_CLIENT_ID = os.getenv('spotifyID')
        SPOTIFY_CLIENT_SECRET = os.getenv('spotifySecret')
        SPOTIFY_REDIRECT_URI = "http://127.0.0.1:1410"  # Check your API port number
        SCOPE = "playlist-modify-public playlist-modify-private user-read-private user-read-email"

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id = SPOTIFY_CLIENT_ID,
            client_secret = SPOTIFY_CLIENT_SECRET,
            redirect_uri = SPOTIFY_REDIRECT_URI,
            scope = SCOPE
        ))

        self.userid = self.sp.current_user()["id"]
        self.playlist_name = os.getenv('spotifyPlaylistName')
        self.description = "Playlist created and updated automatically."
        self.playlistID = os.getenv('spotifyPlaylistID')

    def create_playlist(self):
        playlist = self.sp.user_playlist_create(
            self.userid,
            self.playlist_name,
            public=True,
            description=self.description
        )
        
        return playlist["id"]


    def get_playlist_songs(self):

        playlist = self.sp.playlist_items(self.playlistID, limit=100)
        playlist = playlist['items']
        uri_list = [item['track']['uri'] for item in playlist if item['track'] is not None]
        return uri_list

    
    def add_to_playlist(self, track_uris):

        # Add Songs to the playlist
        if track_uris:
            self.sp.playlist_add_items(self.playlistID, track_uris)
            print(f"✅ {len(track_uris)} songs added to playlist '{self.playlist_name}' successfully!")
        else:
            print("❌ - No songs found to add to the playlist.")

    def remove_from_playlist(self, track_uris):
            
        # Remove songs from the playlist
        if track_uris:
            self.sp.playlist_remove_all_occurrences_of_items(self.playlistID, track_uris)
            print(f"✅ {len(track_uris)} songs removed from playlist '{self.playlist_name}' successfully!")
        else:
            print("❌ - No songs found to remove from the playlist.")
    
    def search_song(self, track_name, artist_name=None):

        query = f"track:{track_name}"

        if artist_name:
            query += f" artist:{artist_name}"

        try:

            results = self.sp.search(q=query, type="track", limit=1)
        except:

            results = self.sp.search(q=query, type="track", limit=1)

        tracks = results.get("tracks", {}).get("items", [])
        if tracks:
            track_uri = tracks[0]['uri']
            track_name_spotify = tracks[0]['name']
            track_artist_spotify = tracks[0]['artists'][0]['name']
            return track_uri, track_name_spotify, track_artist_spotify  # Returns the track URI

        else:
            track_uri = None
            track_name_spotify = None
            track_artist_spotify = None
            return track_uri, track_name_spotify, track_artist_spotify


def get_reddit_posts():
    
    print("🔄 Fetching Reddit...")

    reddit = praw.Reddit(
        client_id=os.getenv('redditID'),
        client_secret=os.getenv('redditSecret'),
        user_agent='MLadika'
    )

    subreddit_name = 'Metalcore'
    subreddit = reddit.subreddit(subreddit_name)

    # Calculate timestamp for 7 days ago
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    one_week_ago_timestamp = int(one_week_ago.timestamp())
    date_object = datetime.now()
    month_name_full = date_object.strftime("%B")

    # Fetch posts from the last week
    lists = []

    for submission in subreddit.new(limit=None):

        if submission.created_utc >= one_week_ago_timestamp and f'Weekly Release Thread {month_name_full}' in submission.title:
            print(f"🔄 - Found {submission.title}...")
            title = submission.title.split(' ')
            month = title[3]
            day = title[4]
            day = day.replace('th', '')
            day = day.replace(',','')
            year = title[5]
            date = f'{day}/{month}/{year}'

            post_list = submission.selftext.split('\n')
            while '' in post_list:
                post_list.remove('')

            lists.append(post_list)

    data = []
    current_category = None

    for sublist in lists:
        for item in sublist:
            if " - " in item:
                band, song = item.split(" - ")
                data.append({"Band": band, "Song": song, "Category": current_category})

            else:
                current_category = item

        df_songs = pd.DataFrame(data)
        df_songs['Date'] = date
        df_songs = df_songs.loc[df_songs['Category'] != '**Albums/EPs**']
        
    return df_songs

load_dotenv(".env")

df_songs = get_reddit_posts()

# Open blacklist from JSON
BLACKLIST_FILE = 'blacklist.json'
if os.path.exists(BLACKLIST_FILE):
    with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
        blacklist_bands = set(json.load(f))
else:
    blacklist_bands = set()

spotify = ConnectSpotify()

track_uris = []
songs_consulted_dict = {}

# Search for songs and create a DF with URIs
if not df_songs.empty:
    os.system('cls')
   
    for _, row in df_songs.iterrows():
        track_name = row["Song"]  # Song name
        artist_name = row.get("Band")  # Artist name

        # Remove 'feat' and anything after it from the track name
        if 'feat' in track_name:
            track_name = track_name.split('feat')[0].strip()

        # Search for the song URI
        track_uri, track_name_spotify, track_artist_spotify = spotify.search_song(track_name=track_name, artist_name=artist_name)
        if track_uri:
            track_uris.append(track_uri)
            songs_consulted_dict[track_artist_spotify] = track_name_spotify
        else:
            print(f"⚠️ - Song not found: {artist_name} - {row['Song']}")

else:
    print("😢 - No new songs found.")
    
df_final_songs = pd.DataFrame(songs_consulted_dict.items(), columns=['Band', 'Song'])
df_final_songs['uri'] = track_uris

# Read playlist
playlist = spotify.get_playlist_songs()

# Remove songs already in the playlist
filtered_df = df_final_songs[~df_final_songs['uri'].isin(playlist)]
print(f"🔍 - Songs filtered!")

# Remove blacklisted bands
filtered_df = filtered_df[~filtered_df['Band'].isin(blacklist_bands)]

# Remove duplicates
filtered_df = filtered_df.drop_duplicates(subset=['Song'], keep='last')

# Save to CSV (or handle as needed)
filtered_df.to_csv('songs.csv', index=False)

spotify.remove_from_playlist(playlist)
print("🧹 - Playlist cleaned")
spotify.add_to_playlist(filtered_df['uri'].tolist())
print('✅ - Playlist Updated!')