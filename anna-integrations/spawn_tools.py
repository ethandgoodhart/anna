import requests
import os
import json
from dotenv import load_dotenv

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "play_track",
            "description": "Play a specific track on Spotify by name",
            "parameters": {
                "type": "object",
                "properties": {
                    "track_name": {
                        "type": "string",
                        "description": "The name of the track to play",
                    },
                },
                "required": ["track_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "next_track",
            "description": "Skip to the next track in Spotify",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "previous_track",
            "description": "Go back to the previous track in Spotify",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "play_random_playlist",
            "description": "Play a random playlist from your Spotify library",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "play_playlist",
            "description": "Play a specific Spotify playlist by search query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find the playlist",
                    },
                },
                "required": ["query"],
            },
        },
    },
]


INSTRUCTIONS = f"""Say hello to the user and help them with their requests."""

if __name__ == "__main__":
    print(os.getenv("TAVUS_API_KEY"))