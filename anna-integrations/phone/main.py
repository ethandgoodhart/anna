import fastapi
import requests
import asyncio
app = fastapi.FastAPI()

prompt = "You are a digital assistant. But a friendly one, a little funny sometimes, laugh, smile, be helpful. you just have to make sure that you do the things that the user wants you to do. You are at Treehacks, a hackathon at Stanford, and made by a team of ambitious students wanting to revolutionalise "
first_message = "Hello, i am Ethan, how are you?"


@app.get("/call")
async def call(phone_number: str):
    response = requests.post(
        "http://localhost:9000/outbound-call",
        json={"prompt": prompt, "first_message": first_message, "number": phone_number},
    )
    

    print(response.json())

    return {"called": phone_number}

if __name__ == "__main__":
    asyncio.run(call("+12148098165"))

