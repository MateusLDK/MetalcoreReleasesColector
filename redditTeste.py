import praw
import spotipy
import os
import pandas as pd
from tqdm.auto import tqdm
from spotipy.oauth2 import SpotifyOAuth
from dotenv   import load_dotenv
from datetime import datetime, timedelta

class ConectarSpotify():

    def __init__(self):

        SPOTIFY_CLIENT_ID = os.getenv('spotifyID')
        SPOTIFY_CLIENT_SECRET = os.getenv('spotifySecret')
        SPOTIFY_REDIRECT_URI = "http://127.0.0.1:1410"  # Verificar qual é o numero na sua API
        SCOPE = "playlist-modify-public playlist-modify-private user-read-private user-read-email"

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id = SPOTIFY_CLIENT_ID,
            client_secret = SPOTIFY_CLIENT_SECRET,
            redirect_uri = SPOTIFY_REDIRECT_URI,
            scope = SCOPE
        ))

        self.userid = self.sp.current_user()["id"]
        self.playlist_name = "LSMP - Ladika Smart Metalcore Playlist"
        self.description = "Playlist criada e atualizada automaticamente."
        self.playlistID = '276lrZKj397C8zSuq4bGjd'


    def criarPlaylist(self):

        playlist = self.sp.user_playlist_create(
            self.userid, self.playlist_name, public=True, description=self.description)
        return playlist["id"]  # Retorna o ID da playlist
    

    def consultarPlaylist(self):

        playlist = self.sp.playlist_items(self.playlistID, limit=100)
        playlist = playlist['items']
        playlist = [item['track']['name'] for item in playlist if item['track'] is not None]
        return playlist

    
    def adicionarNaPlaylist(self, track_uris):

        # Adicionar as músicas à playlist
        if track_uris:
            self.sp.playlist_add_items(self.playlistID, track_uris)
            print(f"✅ {len(track_uris)} músicas adicionadas à playlist '{self.playlist_name}' com sucesso!")
        else:
            print("Nenhuma música foi encontrada para adicionar à playlist.")

    def removerDaPlaylist(self, track_uris):
            
        # Remover as músicas da playlist
        if track_uris:
            self.sp.playlist_remove_all_occurrences_of_items(self.playlistID, track_uris)
            print(f"✅ {len(track_uris)} músicas removidas da playlist '{self.playlist_name}' com sucesso!")
        else:
            print("Nenhuma música foi encontrada para remover da playlist.")
    
    def procurarMusica(self, track_name, artist_name=None):

        query = f"track:{track_name}"

        if artist_name:
            query += f" artist:{artist_name}"

        results = self.sp.search(q=query, type="track", limit=1)
        tracks = results.get("tracks", {}).get("items", [])
        if tracks:
            trackUri = tracks[0]['uri']
            trackName = tracks[0]['name']
            trackArtist = tracks[0]['artists'][0]['name']
            return trackUri, trackName, trackArtist  # Retorna o URI da música
        
        else:
            trackUri = None
            trackName = None
            trackArtist = None
            return trackUri, trackName, trackArtist  # Retorna o URI da música


def consultarReddit():

    reddit = praw.Reddit(
        client_id=os.getenv('redditID'),
        client_secret=os.getenv('redditSecret'),
        user_agent='MLadika'
    )

    subreddit_name = 'Metalcore'
    subreddit = reddit.subreddit(subreddit_name)

    # Calcula o timestamp de 7 dias atrás
    one_week_ago = datetime.utcnow() - timedelta(days=5)
    one_week_ago_timestamp = int(one_week_ago.timestamp())

    # Busca posts da última semana
    listas = []
    os.system('cls')
    with tqdm(subreddit.new(limit=None)) as pbar:
        for submission in subreddit.new(limit=None):

            if submission.created_utc >= one_week_ago_timestamp and 'Weekly Release Thread' in submission.title:
                titulo = submission.title.split(' ')
                mes = titulo[3]
                dia = titulo[4]
                dia = dia.replace('th', '')
                dia = dia.replace(',','')
                ano = titulo[5]
                data = f'{dia}/{mes}/{ano}'

                lista = submission.selftext.split('\n')
                while '' in lista:
                    lista.remove('')

                listas.append(lista)

            pbar.update(1)

    dados = []
    categoriaAtual = None

    for subLista in listas:
        for item in subLista:
            if " - " in item:
                banda, musica = item.split(" - ")
                dados.append({"Banda": banda, "Música": musica, "Categoria": categoriaAtual})

            else:
                categoriaAtual = item


    #dados[data] = data

    dfMusicas = pd.DataFrame(dados)
    dfMusicas['Data'] = data
    bandasBlackList = []

    try:
        planilhaMusicas   = pd.read_excel('musics.xlsx', sheet_name='Musicas')
        planilhaBlackList = pd.read_excel('musics.xlsx', sheet_name='BlackList')
        bandasBlackList = planilhaBlackList['Banda'].tolist()

    except: 
        planilhaMusicas = pd.DataFrame()

    dfFinal = pd.concat([dfMusicas, planilhaMusicas]).drop_duplicates().reset_index(drop=True)
    dfFinal = dfFinal[~dfFinal['Banda'].isin(bandasBlackList)]

    dfFinal.to_excel('musics.xlsx', index=False, header=True)
    return dfFinal

load_dotenv(".env")

dfMusicas = consultarReddit()
spotify = ConectarSpotify()

dfFiltrado = dfMusicas.loc[dfMusicas['Categoria'] != '**Albums/EPs**']

track_uris = []
dictMusicasFinal = {}

if not dfFiltrado.empty:
    os.system('cls')
    with tqdm(total=len(dfFiltrado), unit="música") as pbar:
        for _, row in dfFiltrado.iterrows():

            track_name = row["Música"]  # Nome da música
            artist_name = row.get("Banda")  # Nome do artista

            # Buscar o URI da música
            track_uri, track_name_spotify, track_artist_spotify = spotify.procurarMusica(track_name=track_name, artist_name=artist_name)
            if track_uri:
                track_uris.append(track_uri)
                dictMusicasFinal[track_artist_spotify] = track_name_spotify

            else:
                pass #print(f"⚠️ Música não encontrada: {artist_name} - {track_name}")

            pbar.update(1)
        
else:
    print("Nenhuma música nova encontrada.")
    
dfMusicasFinal = pd.DataFrame(dictMusicasFinal.items(), columns=['Banda', 'Música'])
dfMusicasFinal['uri'] = track_uris


playlistAtual = spotify.consultarPlaylist()
playlistAtual = [musica.lower() for musica in playlistAtual]
dfFiltrado = dfFiltrado[~dfFiltrado['Música'].isin(dfMusicasFinal['Música'])]
print(dfFiltrado)
dfFiltrado.to_excel('musicasFinal.xlsx', index=False, header=True)

spotify.adicionarNaPlaylist(dfFiltrado['uri'].tolist())

removeTracks = []
for musica in playlistAtual:

    # Buscar o URI da música
    removeTrack = spotify.procurarMusica(track_name=musica)
    if removeTrack:
        removeTracks.append(removeTrack)
    else:
        print(f"⚠️ Música não encontrada: {track_name}")


spotify.removerDaPlaylist(removeTracks)
#spotify.criarPlaylist()