import os
import time
from typing import Generator
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from openai import OpenAI
import requests
from spawn_tools import TOOLS
from openai.types.chat.chat_completion_chunk import (
    ChatCompletionChunk,
    Choice,
    ChoiceDelta,
)

import json
import traceback
from dotenv import load_dotenv

from daily import CallClient, Daily

load_dotenv()

function_mapping = {
    "play_track": "spotify",
    "next_track": "spotify",
    "previous_track": "spotify",
    "play_random_playlist": "spotify",
    "play_playlist": "spotify",
    "search": "websearch",
    "send_message": "imessage",
    "check_new_messages": "imessage",
    "get_messages": "imessage",
}

app = FastAPI()
NGROK_URL = os.getenv("NGROK_URL", "")


def request_handler(route: str, data: dict):
    service = function_mapping[route]
    # Convert spaces to %20 in track name if present
    if "track_name" in data:
        data["track_name"] = data["track_name"].replace(" ", "%20")
        
    res = requests.get(
        f"http://localhost:8000/{service}/{route.replace('_', '-')}", params=data
    )
    data = res.json()
    print(data)


    res_data = {
        "event": "route",
        "data": res.json(),
    }

    llm_string = f"Successfully made a request to {route}"

    chunk = ChatCompletionChunk(
        **{
            "id": "0",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "gpt-4o-mini",
            "choices": [
                Choice(
                    **{
                        "index": 0,
                        "finish_reason": "stop",
                        "delta": ChoiceDelta(**{"content": llm_string}),
                    }
                )
            ],
        }
    )

    return res_data, chunk


def get_conversation_url():
    url = "https://tavusapi.com/v2/conversations"
    headers = {"x-api-key": os.getenv("TAVUS_API_KEY")}
    response = requests.request("GET", url, headers=headers)
    print(response.json())
    return response.json()["data"][0]["conversation_url"]


call_client = None
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.post("/chat/completions")
async def chat_completions(request: Request):
    room_url = get_conversation_url()
    try:
        global call_client
        if not call_client:
            try:
                Daily.init()
                call_client = CallClient()
                call_client.join(room_url)
                print(f"Joined room: {room_url}")
            except Exception as e:
                print(f"Error joining room: {e}")
                raise

        # Get JSON data from request
        data = await request.json()

        # Extract relevant information from the request
        messages = data.get("messages", [])
        model = "gpt-4o-mini"
        tools = data.get("tools", TOOLS)

        cerebras_response = client.chat.completions.create(
            model=model, messages=messages, stream=True, tools=tools, tool_choice="auto"
        )

        # Replace Flask's stream_with_context with async generator
        async def generate() -> Generator[str, None, None]:
            try:
                total_response = ""
                current_function = None
                current_tool_call_id = None
                function_args_buffer = ""

                for chunk in cerebras_response:
                    print(chunk)
                    if chunk.choices[0].delta.tool_calls is not None:
                        tool_call = chunk.choices[0].delta.tool_calls[0]

                        if tool_call.function.name:
                            current_function = tool_call.function.name
                            current_tool_call_id = tool_call.id

                        if tool_call.function.arguments:
                            function_args_buffer += tool_call.function.arguments

                        # Yield the tool call chunks as well
                        yield f"data: {chunk.model_dump_json()}\n\n"

                    # When we get the finish_reason="tool_calls", the function call is complete
                    if chunk.choices[0].finish_reason == "tool_calls":
                        try:
                            print(f"FUNCTION ARGS BUFFER: {function_args_buffer}")
                            function_args = json.loads(function_args_buffer)
                            if current_function in function_mapping:
                                print(
                                    f"RUNNING {current_function}({', '.join([f'{k}={v}' for k, v in function_args.items()])})"
                                )
                                app_message, llm_response = request_handler(
                                    current_function, function_args
                                )
                                print(f"SENDING APP MESSAGE: {app_message}")
                                call_client.send_app_message(app_message)

                                # # Where the TODO comment was - Format response for UI
                                # formatted_response = {}
                                # if current_function in function_mapping:
                                #     service = function_mapping[current_function]
                                    
                                #     if service == "spotify":
                                #         formatted_response = {
                                #             "type": "music",
                                #             "data": {
                                #                 "songTitle": app_message["data"].get("track_name", "Unknown Track"),
                                #                 "artist": app_message["data"].get("artist_name", "Unknown Artist"),
                                #                 "currentTime": "0:00",
                                #                 "duration": app_message["data"].get("duration", "0:00"),
                                #                 "progress": app_message["data"].get("progress_ms", 0) / app_message["data"].get("duration_ms", 1) * 100 if app_message["data"].get("duration_ms") else 0,
                                #                 "albumArt": app_message["data"].get("album_art", "default_album_art_url")
                                #             }
                                #         }
                                #     elif service == "imessage":
                                #         formatted_response = {
                                #             "type": "notification",
                                #             "data": {
                                #                 "userName": app_message["data"].get("sender", "Unknown User"),
                                #                 "message": app_message["data"].get("message", "No message content"),
                                #                 "notificationCount": app_message["data"].get("unread_count", 1)
                                #             }
                                #         }
                                #     elif service == "websearch":
                                #         formatted_response= {
                                #             "type": "websearch",
                                #             "data": {
                                                
                                #             }
                                #         }
                                    
                                #     # Update app_message with formatted response
                                #     app_message["data"] = formatted_response
                                    
                                #     # Send the formatted message through the call client
                                #     # Send webhook to notify UI of updates
                                #     try:
                                #         requests.post("http://localhost:8787/webhook", json=app_message)
                                #     except Exception as e:
                                #         print(f"Failed to send webhook: {e}")

                                yield f"data: {llm_response.model_dump_json()}\n\n"

                                # TODO: Send webhook here with function execution results
                                # Example webhook data could include:
                                # - current_function
                                # - function_args
                                # - app_message
                                # - llm_response
                                print(current_function, function_args, app_message, llm_response)

                                # Add the tool call result back to messages and continue the conversation
                                messages.append(
                                    {
                                        "role": "assistant",
                                        "content": None,
                                        "tool_calls": [
                                            {
                                                "id": current_tool_call_id,
                                                "function": {
                                                    "name": current_function,
                                                    "arguments": json.dumps(
                                                        function_args
                                                    ),
                                                },
                                                "type": "function",
                                            }
                                        ],
                                    }
                                )
                                messages.append(
                                    {
                                        "role": "tool",
                                        "content": llm_response.choices[
                                            0
                                        ].delta.content,
                                        "tool_call_id": current_tool_call_id,
                                    }
                                )

                                # Create a new completion to continue the conversation
                                continuation_response = client.chat.completions.create(
                                    model=model,
                                    messages=messages,
                                    stream=True,
                                    tools=tools,
                                    tool_choice="auto",
                                )

                                # Process the continuation response
                                for cont_chunk in continuation_response:
                                    yield f"data: {cont_chunk.model_dump_json()}\n\n"

                        except json.JSONDecodeError as e:
                            print(
                                f"Error parsing function arguments: {function_args_buffer}"
                            )
                            print(f"Error: {e}")

                        # Reset buffers after handling the function
                        current_function = None
                        current_tool_call_id = None
                        function_args_buffer = ""

                    # Handle normal content chunks
                    if chunk.choices[0].delta.content is not None:
                        if (
                            "FN_CALL=True" in chunk.choices[0].delta.content
                            or "FN_CALL=False" in chunk.choices[0].delta.content
                        ):
                            continue
                        total_response += chunk.choices[0].delta.content
                        yield f"data: {chunk.model_dump_json()}\n\n"
                print(f"LLM RESPONSE: {total_response}")
            except Exception as e:
                print(traceback.format_exc())
                yield json.dumps({"error": str(e)})

        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        print(traceback.format_exc())
        return StreamingResponse(
            json.dumps({"error": str(e)}),
            media_type="application/json",
            status_code=500,
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
