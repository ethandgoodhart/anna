import os
import random
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import openai
from pydantic import BaseModel

class PlaylistId(BaseModel):
    playlist_id: str

def get_openai_client():
    return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def reauthorize_spotify():
    """
    Reauthorize Spotify client if token is revoked
    """
    scope_list = [
        "user-modify-playback-state",
        "user-read-playback-state",
        "user-library-read",
        "streaming",
        "app-remote-control",
        "user-read-currently-playing",
        "playlist-read-private",
    ]
    scope = ", ".join(scope_list)
    
    return Spotify(
        auth_manager=SpotifyOAuth(
            scope=scope,
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        )
    )

async def play_track(spotify: Spotify, uri: str) -> Spotify:
    """
    plays the track with the given uri
    """
    try:
        spotify.volume(50)
        return spotify.start_playback(uris=[uri])
    except Exception as e:
        if "The access token expired" in str(e):
            spotify = reauthorize_spotify()
            return spotify.start_playback(uris=[uri])
        raise e
    
async def pause_track(spotify: Spotify) -> Spotify:
    """
    pauses the current track
    """
    spotify.volume(0)
    await spotify.pause_playback()    
        

async def get_current_track(spotify: Spotify) -> Spotify:
    """
    returns the current track
    """
    try:
        res = spotify.current_playback()
    except Exception as e:
        if "The access token expired" in str(e):
            spotify = reauthorize_spotify()
            res = spotify.current_playback()
        else:
            raise e

    name = res["item"]["name"]
    artist = res["item"]["artists"][0]["name"]
    album = res["item"]["album"]["name"]
    duration = res["item"]["duration_ms"]
    image = res["item"]["album"]["images"][0]["url"]
    uri = res["item"]["uri"]

    return {
        "name": name,
        "artist": artist,
        "duration": duration,
        "album": album,
        "image": image,
        "uri": uri,
    }

async def get_track_uri(spotify: Spotify, query: str) -> str:
    """
    returns the uri of the track with the given name
    """
    try:
        results = spotify.search(q=query, type="track")
    except Exception as e:
        if "The access token expired" in str(e):
            spotify = reauthorize_spotify()
            results = spotify.search(q=query, type="track")
        else:
            raise e

    name = results["tracks"]["items"][0]["name"]
    artist = results["tracks"]["items"][0]["artists"][0]["name"]
    album = results["tracks"]["items"][0]["album"]["name"]
    duration = results["tracks"]["items"][0]["duration_ms"]
    image = results["tracks"]["items"][0]["album"]["images"][0]["url"]
    uri = results["tracks"]["items"][0]["uri"]

    response = {
        "name": name,
        "artist": artist,
        "duration": duration,
        "album": album,
        "image": image,
        "uri": uri,
    }

    return response

async def get_user_playlists(spotify: Spotify) -> tuple[list, list]:
    """
    returns a list of the users playlists
    """
    playlists = []
    playlist_ids = []
    offset = 0
    
    try:
        results = spotify.current_user_playlists(limit=50, offset=offset)
    except Exception as e:
        if "The access token expired" in str(e):
            spotify = reauthorize_spotify()
            results = spotify.current_user_playlists(limit=50, offset=offset)
        else:
            raise e
            
    while len(results["items"]) != 0:
        for i in range(len(results["items"])):
            playlists.append(results["items"][i]["name"])
            playlist_ids.append(results["items"][i]["id"])
        offset += 50
        results = spotify.current_user_playlists(limit=50, offset=offset)

    return playlists, playlist_ids

async def play_playlist(spotify: Spotify, playlist_id: str) -> Spotify:
    """
    plays the playlist with the given id
    """
    try:
        return spotify.start_playback(context_uri=f"spotify:playlist:{playlist_id}")
    except Exception as e:
        if "The access token expired" in str(e):
            spotify = reauthorize_spotify()
            return spotify.start_playback(context_uri=f"spotify:playlist:{playlist_id}")
        raise e

async def next_track(spotify: Spotify) -> Spotify:
    """
    skips to the next track
    """
    try:
        spotify.next_track()
    except Exception as e:
        if "The access token expired" in str(e):
            spotify = reauthorize_spotify()
            spotify.next_track()
        else:
            raise e
    return await get_current_track(spotify)

async def previous_track(spotify: Spotify) -> Spotify:
    """
    goes back to the previous track
    """
    try:
        spotify.previous_track()
    except Exception as e:
        if "The access token expired" in str(e):
            spotify = reauthorize_spotify()
            spotify.previous_track()
        else:
            raise e
    return await get_current_track(spotify)

async def play_random_playlist(spotify: Spotify) -> Spotify:
    """
    plays a random playlist
    """
    playlists, playlist_ids = await get_user_playlists(spotify)
    await play_playlist(
        spotify, playlist_ids[random.randint(0, len(playlist_ids) - 1)]
    )

    return await get_current_track(spotify)

async def play_playlist_from_query(spotify: Spotify, query: str) -> Spotify:
    """
    plays a playlist with the given query
    """
    client = get_openai_client()
    
    user_playlists, user_playlist_ids = await get_user_playlists(spotify)
    
    playlist_mappings = "\n".join([f"{name}: {id}" for name, id in zip(user_playlists, user_playlist_ids)])

    res = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{
            "role": "user", 
            "content": f"You are a playlist selector. Given a query and a list of playlists with their IDs, return the ID of the playlist that best matches the query. Only return the playlist ID, nothing else.\n\nQuery: {query}\n\nPlaylists:\n{playlist_mappings}"
            },
        ],
        response_format=PlaylistId,
    )

    await play_playlist(spotify, res.choices[0].message.parsed.playlist_id)

    return await get_current_track(spotify)
