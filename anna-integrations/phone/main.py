import fastapi
import requests
import asyncio
app = fastapi.FastAPI()

prompt = "You are a car sales agent. You are calling to sell a new car to the customer. Be friendly and professional and answer all questions."
first_message = "Hello, my name is Eric, I heard you were looking for a new car! What model and color are you looking for?"


@app.get("/call")
async def call(phone_number: str):
    response = requests.post(
        "http://localhost:9000/outbound-call",
        json={"prompt": prompt, "first_message": first_message, "number": phone_number},
    )
    

    print(response.json())

    return {"called": phone_number}

if __name__ == "__main__":
    # import uvicorn

    # uvicorn.run(app, host="0.0.0.0", port=8000)

    asyncio.run(call("+12148098165"))

