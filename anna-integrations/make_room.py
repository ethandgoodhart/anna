import requests
import os
from dotenv import load_dotenv
import time
load_dotenv()

async def make_room():
    url = "https://tavusapi.com/v2/conversations"

    payload = {
        "persona_id": "p91850b706d1",
        "replica_id": "rcefb7292e",
        "conversation_name": "A Meeting with Hassaan",
        "conversational_context": "You are about to talk to Hassaan, one of the cofounders of Tavus. He loves to talk about AI, startups, and racing cars.",
        "custom_greeting": "Hey there Hassaan, long time no see!",
        "properties": {
            "max_call_duration": 60*2,
            "participant_left_timeout": 60,
            "participant_absent_timeout": 300,
        }
    }
    headers = {
        "x-api-key": os.getenv("TAVUS_API_KEY"),
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.json())

    return response.json()["conversation_id"]

async def delete_room(conversation_id: str):
    url = f"https://tavusapi.com/v2/conversations/{conversation_id}"

    headers = {
        "x-api-key": os.getenv("TAVUS_API_KEY")
    }

    response = requests.request("DELETE", url, headers=headers)
    print(response.json())

    return response.json()

if __name__ == "__main__":
    import asyncio
    conversation_id = asyncio.run(make_room())
