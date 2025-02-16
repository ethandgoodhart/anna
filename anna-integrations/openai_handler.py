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
    "pause_track": "spotify",
    "search": "websearch",
    "send_message": "imessage",
    "check_new_messages": "imessage",
    "get_messages": "imessage",
    "call": "phone",
    "start_holochat": "holochat",
    "upcoming_assignments": "canvas"
}

# Track last function call times
last_function_calls = {}

app = FastAPI()
NGROK_URL = os.getenv("NGROK_URL", "")


def get_conversation_url():
    url = "https://tavusapi.com/v2/conversations"
    headers = {"x-api-key": os.getenv("TAVUS_API_KEY")}
    response = requests.request("GET", url, headers=headers)
    print(response.json())
    return response.json()["data"][0]["conversation_url"]

def get_conversation_id():
    url = "https://tavusapi.com/v2/conversations"
    headers = {"x-api-key": os.getenv("TAVUS_API_KEY")}
    response = requests.request("GET", url, headers=headers)
    print(response.json())
    return response.json()["data"][0]["conversation_id"]

def request_handler(route: str, data: dict):
    service = function_mapping[route]
    # For upcoming_assignments, we don't need to pass any params
    if route == "upcoming_assignments" or route == "pause_track":
        res = requests.get(f"http://localhost:8000/{service}/{route.replace('_', '-')}")
    else:
        res = requests.get(
            f"http://localhost:8000/{service}/{route.replace('_', '-')}", params=data
        )

    if res.text == "":
        return None, None
    response_data = res.text
    print("responseeeee", response_data)

    hi = json.loads(response_data)
    print(hi)

    res_data = {
        "event": "route",
        "data": response_data,
    }

    llm_string = f"Successfully made a request to {route}"
    if route == "upcoming_assignments":
        assignments = json.loads(response_data)
        llm_string = "Here are your upcoming assignments:\n"
        for assignment in assignments:
            llm_string += f"- {assignment['assignment']} for {assignment['class']}, due {assignment['due_at']}\n"

    chunk = ChatCompletionChunk(
        **{
            "id": "0",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "gpt-4o",
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
        model = "gpt-4o"
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
                            # Reset buffer when we start a new function call
                            current_function = tool_call.function.name
                            current_tool_call_id = tool_call.id
                            function_args_buffer = ""

                        if tool_call.function.arguments:
                            function_args_buffer += tool_call.function.arguments

                        # Yield the tool call chunks as well
                        yield f"data: {chunk.model_dump_json()}\n\n"

                    # When we get the finish_reason="tool_calls", the function call is complete
                    if chunk.choices[0].finish_reason == "tool_calls":
                        try:
                            print(f"FUNCTION ARGS BUFFER: {function_args_buffer}")
                            
                            # Initialize empty dict for functions that don't need arguments
                            function_args = {}
                            
                            # Only try to parse if there's actual content and not empty brackets
                            if function_args_buffer.strip() and function_args_buffer.strip() != "{}":
                                cleaned_buffer = function_args_buffer.replace("{}", "").strip()
                                
                                try:
                                    function_args = json.loads(cleaned_buffer)
                                except json.JSONDecodeError:
                                    start_idx = cleaned_buffer.find("{")
                                    end_idx = cleaned_buffer.find("}") + 1
                                    if start_idx != -1 and end_idx != -1:
                                        function_args = json.loads(cleaned_buffer[start_idx:end_idx])
                            
                            # Special handling for functions that don't need arguments
                            # if current_function == "upcoming_assignments":
                            #     function_args = {}  # Explicitly set empty dict for this function

                            # Check if function was called recently
                            current_time = time.time()
                            if current_function in last_function_calls:
                                if current_time - last_function_calls[current_function] < 10:
                                    print(f"Skipping {current_function} - called too recently")
                                    continue
                            
                            if current_function in function_mapping:
                                print(
                                    f"RUNNING {current_function}({', '.join([f'{k}={v}' for k, v in function_args.items()])})"
                                )
                                app_message, llm_response = request_handler(
                                    current_function, function_args
                                )
                                
                                # Update last call time
                                last_function_calls[current_function] = current_time
                                
                                print(f"SENDING APP MESSAGE: {app_message}")
                                call_client.send_app_message({
                                    "message_type": "conversation",
                                    "event_type": "conversation.overwrite_llm_context", 
                                    "conversation_id": "c123456",
                                    "properties": {
                                        "context": app_message
                                    }
                                })

                                # Format response for UI
                                formatted_response = {}
                                if current_function in function_mapping:
                                    service = function_mapping[current_function]
                                    
                                    if service == "spotify":
                                        spotify_data = json.loads(app_message['data'])
                                        formatted_response = {
                                            "type": "music",
                                            "data": {
                                                "songTitle": spotify_data["name"],
                                                "artist": spotify_data["artist"],
                                                "currentTime": "0:00",
                                                "duration": spotify_data["duration"],
                                                "progress": 0,
                                                "albumArt": spotify_data["image"]
                                            }
                                        }
                                    elif service == "imessage":
                                        print(app_message)
                                        imessage_data = json.loads(app_message["data"])
                                        formatted_response = {
                                            "type": "notification",
                                            "data": {
                                                "userName": imessage_data.get("userName", "Unknown User"),
                                                "message": imessage_data.get("message", "No message content"),
                                                "notificationCount": 1
                                            }
                                        }
                                    elif service == "websearch":
                                        search_data = json.loads(app_message['data'])
                                        formatted_response = {
                                            "type": "websearch",
                                            "data": {
                                                "results": search_data["results"],
                                                "query": search_data["autoprompt_string"],
                                                "searchType": search_data["resolved_search_type"]
                                            }
                                        }
                                    elif service == "holochat":
                                        formatted_response = {
                                            "type": "holochat",
                                            "data": ""
                                        }
                                    # elif service == "canvas":
                                    #     assignments_data = json.loads(app_message['data'])
                                    #     formatted_response = {
                                    #         "type": "assignments",
                                    #         "data": {
                                    #             "assignments": assignments_data
                                    #         }
                                    #     }
                                    
                                    # Send the formatted message through the call client
                                    # Send webhook to notify UI of updates
                                    try:
                                        requests.post("http://localhost:3000/webhook", json=formatted_response)
                                    except Exception as e:
                                        print(f"Failed to send webhook: {e}")

                                yield f"data: {llm_response.model_dump_json()}\n\n"

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
            finally:
                function_args_buffer = ""
                current_function = None
                current_tool_call_id = None

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
