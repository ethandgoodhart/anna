from openai import OpenAI

import os


async def call_openai_endpoint(data: dict):
    url = "https://f54f-2607-f6d0-ced-5bb-9d89-5c92-9244-66fb.ngrok-free.app"

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

    data = {"messages": [{"role": "user", "content": "Play daily duppy central cee"}]}
    print(asyncio.run(call_openai_endpoint(data)))
