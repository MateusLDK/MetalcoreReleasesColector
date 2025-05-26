# Metalcore Releases Collector

This project automatically collects new metalcore releases from Reddit and updates a Spotify playlist with the latest tracks.

## Setup Instructions

1. **Clone the repository and install dependencies**
   - Make sure you have Python 3.x installed.
   - Install the required packages:
     ```bash
     pip install -r requirements.txt
     ```

2. **Create a `.env` file in the main folder**
   - The file must contain the following keys:
     ```env
     redditID=YOUR_REDDIT_CLIENT_ID
     redditSecret=YOUR_REDDIT_CLIENT_SECRET
     spotifyID=YOUR_SPOTIFY_CLIENT_ID
     spotifySecret=YOUR_SPOTIFY_CLIENT_SECRET
     spotifyPlaylistID=  # Leave blank for first run
     ```
   - You need to generate your own ID and Secret for both Reddit and Spotify. Fill in your `.env` file with these values.

3. **Create your Spotify playlist**
   - Run the `create_playlist.py` file to create a new playlist for your Spotify user:
     ```bash
     python create_playlist.py
     ```
   - The script will create the playlist, print its ID and update the .env key.

4. **Run the main script**
   - Execute `redditTeste.py` to fetch new releases and update your playlist:
     ```bash
     python redditTeste.py
     ```
   - The script will automatically update your playlist with the latest tracks from Reddit.

## Usage Notes
- For best results, run `redditTeste.py` every Friday to ensure your playlist is up to date with the latest weekly releases.

## Blacklist Feature (testing)
- To prevent certain bands from being added to your playlist, use the blacklist feature:
  - Edit the `blacklist.json` file in the project folder.
  - Add the names of bands you want to exclude as strings in the JSON array. Example:
    ```json
    [
        "Bad Band 1",
        "Bad Band 2",
        "Example Blacklisted Band"
    ]
    ```
  - Any band listed in `blacklist.json` will be ignored when updating your playlist.

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License.