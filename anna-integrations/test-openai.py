from openai import OpenAI
import os
from dotenv import load_dotenv
from spawn_tools import TOOLS

load_dotenv()

client = OpenAI(base_url="http://localhost:8080")

messages = [
    {"role": "user", "content": "Can you send a hi to +1 (214) 809-8165"}
]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools= TOOLS,
    tool_choice="auto"
)

print(response)
