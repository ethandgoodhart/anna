import random
from spotipy import Spotify


async def play_track(spotify: Spotify, uri: str) -> Spotify:
    """
    plays the track with the given uri
    """
    return spotify.start_playback(uris=[uri])


async def get_current_track(spotify: Spotify) -> Spotify:
    """
    returns the current track
    """
    res = spotify.current_playback()

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
    results = spotify.search(q=query, type="track")

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
    results = spotify.current_user_playlists(limit=50, offset=offset)
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
    return spotify.start_playback(context_uri=f"spotify:playlist:{playlist_id}")


async def next_track(spotify: Spotify) -> Spotify:
    """
    skips to the next track
    """
    spotify.next_track()
    return await get_current_track(spotify)


async def previous_track(spotify: Spotify) -> Spotify:
    """
    goes back to the previous track
    """
    spotify.previous_track()
    return await get_current_track(spotify)


async def play_random_playlist(spotify: Spotify) -> Spotify:
    """
    plays a random playlist
    """
    playlists, playlist_ids = await get_user_playlists(spotify)
    return await play_playlist(
        spotify, playlist_ids[random.randint(0, len(playlist_ids) - 1)]
    )
