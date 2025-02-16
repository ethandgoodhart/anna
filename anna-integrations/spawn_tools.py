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
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Search the web for information using neural or keyword search",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5
                    },
                    "search_type": {
                        "type": "string",
                        "description": "Type of search to perform",
                        "enum": ["neural", "keyword"],
                        "default": "neural"
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category to filter results",
                        "enum": [
                            "company",
                            "research paper",
                            "news",
                            "pdf",
                            "github",
                            "tweet",
                            "personal site",
                            "linkedin profile",
                            "financial report"
                        ]
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_message",
            "description": "Send an iMessage to a specified phone number",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "The recipient's phone number",
                    },
                    "message_body": {
                        "type": "string",
                        "description": "The message content to send",
                    }
                },
                "required": ["phone_number", "message_body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_recent_messages",
            "description": "Read recent iMessages from the chat history",
            "parameters": {
                "type": "object",
                "properties": {
                    "num_messages": {
                        "type": "integer",
                        "description": "Number of recent messages to retrieve (default: 10)",
                        "default": 10
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_new_messages",
            "description": "Check for new iMessages since the last message ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "last_message_id": {
                        "type": "integer",
                        "description": "The ID of the last message checked (optional)",
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "call",
            "description": "Make a call to a specified phone number",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "The recipient's phone number",
                    }
                },
                "required": ["phone_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pause_track",
            "description": "Pause the current track on Spotify",
        },
    },
]


INSTRUCTIONS = f"""Say hello to the user and help them with their requests."""

if __name__ == "__main__":
    print(os.getenv("TAVUS_API_KEY"))