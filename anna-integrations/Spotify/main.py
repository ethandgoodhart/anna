from spotipy.oauth2 import SpotifyOAuth
import os
import spotipy
from .methods import (
    play_track,
    get_track_uri,
    next_track,
    previous_track,
    play_random_playlist,
    play_playlist_from_query,
)
import fastapi
from dotenv import load_dotenv

load_dotenv("../.env")
print(os.environ)

app = fastapi.FastAPI()

scope_list = [
    "user-modify-playback-state",
    "ugc-image-upload",
    "user-read-playback-state",
    "user-follow-modify",
    "user-read-private",
    "user-follow-read",
    "user-library-modify",
    "user-library-read",
    "streaming",
    "user-read-playback-position",
    "app-remote-control",
    "user-read-email",
    "user-read-currently-playing",
    "user-read-recently-played",
    "playlist-modify-private",
    "playlist-read-collaborative",
    "playlist-read-private",
    "user-top-read",
    "playlist-modify-public",
]
scope = ", ".join(scope_list)

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope=scope,
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    ),
    requests_timeout=300,
)


@app.get("/play-track")
async def play_track_endpoint(track_name: str):
    response = await get_track_uri(spotify=sp, query=track_name)
    await play_track(spotify=sp, uri=response["uri"])
    return response


@app.get("/next-track")
async def next_track_endpoint():
    try:
        res = await next_track(spotify=sp)
        return res
    except Exception as e:
        return {"error": str(e)}


@app.get("/previous-track")
async def previous_track_endpoint():
    try:
        res = await previous_track(spotify=sp)
        return res
    except Exception as e:
        return {"error": str(e)}


@app.get("/play-random-playlist")
async def play_random_playlist_endpoint():
    await play_random_playlist(spotify=sp)
    return {"message": "Playing random playlist"}


@app.get("/play-playlist")
async def play_playlist_endpoint(query: str):
    await play_playlist_from_query(spotify=sp, query=query)
    return {"message": "Playing playlist"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
