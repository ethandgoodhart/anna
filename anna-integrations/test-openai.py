from openai import OpenAI
import os
from dotenv import load_dotenv
from spawn_tools import TOOLS

load_dotenv()

client = OpenAI(base_url="https://proxy.dhr.wtf")

messages = [
    {"role": "user", "content": "Can you play emptiness on spotify"}
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools= TOOLS,
    tool_choice="auto"
)

print(response)
