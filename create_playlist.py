from metalcoreUpdate import ConnectSpotify
from dotenv import load_dotenv, set_key

def create_playlist():
    
    playlist_id = spotifyPlaylist.create_playlist(
        #feel free to change the name and description as you wish :D
        name="Auto Metalcore Playlist", 
        description="playlist updated automatically with new metalcore songs from R/Metalcore.")
    
    if playlist_id:
        print(f"Playlist created successfully with ID: {playlist_id}") #The ID will be saved in the .env file, please dont delete it.
        set_key(".env", "spotifyPlaylistID", playlist_id)
    else:
        print("Failed to create the playlist.")

load_dotenv(".env")
spotifyPlaylist = ConnectSpotify()