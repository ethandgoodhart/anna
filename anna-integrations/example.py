from openai import OpenAI

import os


async def call_openai_endpoint(data: dict):
    url = "http://localhost:8080"

    client = OpenAI(api_key="hi", base_url=url)

    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=data.get("messages", []), stream=True
    )

    response_text = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            response_text += chunk.choices[0].delta.content

    return response_text


if __name__ == "__main__":
    import asyncio

    data = {"messages": [{"role": "user", "content": "play drake"}]}
    print(asyncio.run(call_openai_endpoint(data)))
