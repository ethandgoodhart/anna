import sqlite3
import datetime
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


# Define a Pydantic model for messages
class Message(BaseModel):
    rowid: int
    date: str
    body: str
    phone_number: str
    is_from_me: bool
    cache_roomname: Optional[str]
    group_chat_name: Optional[str]


# Define a Pydantic model for the message sending request
class SendMessageRequest(BaseModel):
    phone_number: str
    message_body: str


def send_imessage(phone_number, message_body):
    clean_phone = "".join(filter(lambda x: x.isdigit() or x == "+", phone_number))
    script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "send_imessage.applescript"
    )

    command = f'osascript "{script_path}" "{clean_phone}" "{message_body}"'

    result = os.system(command)
    if result != 0:
        raise Exception(f"Failed to send message to {phone_number}")
    else:
        print(f"Message sent to {phone_number}")

def get_chat_mapping(db_location):
    conn = sqlite3.connect(db_location)
    cursor = conn.cursor()

    cursor.execute("SELECT room_name, display_name FROM chat")
    result_set = cursor.fetchall()

    mapping = {room_name: display_name for room_name, display_name in result_set}

    conn.close()

    return mapping

def read_messages(db_location, n=None, self_number="Me", human_readable_date=True):
    conn = sqlite3.connect(db_location)
    cursor = conn.cursor()
    query = """
    SELECT message.ROWID, message.date, message.text, message.attributedBody, handle.id, message.is_from_me, message.cache_roomnames
    FROM message
    LEFT JOIN handle ON message.handle_id = handle.ROWID
    """
    if n is not None:
        query += f" ORDER BY message.date DESC LIMIT {n}"
    results = cursor.execute(query).fetchall()

    messages = []

    for result in results:
        rowid, date, text, attributed_body, handle_id, is_from_me, cache_roomname = (
            result
        )

        phone_number = self_number if handle_id is None else handle_id

        if text is not None:
            body = text
        elif attributed_body is None:
            continue
        else:
            attributed_body = attributed_body.decode("utf-8", errors="replace")
            if "NSNumber" in str(attributed_body):
                attributed_body = str(attributed_body).split("NSNumber")[0]
                if "NSString" in attributed_body:
                    attributed_body = str(attributed_body).split("NSString")[1]
                    if "NSDictionary" in attributed_body:
                        attributed_body = str(attributed_body).split("NSDictionary")[0]
                        attributed_body = attributed_body[6:-12]
                        body = attributed_body

        if human_readable_date:
            date_string = "2001-01-01"
            mod_date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
            unix_timestamp = int(mod_date.timestamp()) * 1000000000
            new_date = int((date + unix_timestamp) / 1000000000)
            date = datetime.datetime.fromtimestamp(new_date).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        mapping = get_chat_mapping(db_location)

        try:
            mapped_name = mapping[cache_roomname]
        except:
            mapped_name = None

        messages.append(
            {
                "rowid": rowid,
                "date": date,
                "body": body,
                "phone_number": phone_number,
                "is_from_me": is_from_me,
                "cache_roomname": cache_roomname,
                "group_chat_name": mapped_name,
            }
        )

    conn.close()
    return messages


# FastAPI endpoint to read messages
@app.get("/messages/", response_model=List[Message])
async def get_messages(
    db_location: str = os.getenv("IMESSAGE_DB_LOCATION"), n: Optional[int] = 10
):
    return read_messages(db_location, n)


# FastAPI endpoint to send an iMessage
@app.get("/send-message/")
async def send_message(phone_number: str, message_body: str):
    send_imessage(phone_number, message_body)
    return {"status": "Message sent successfully", "userName": 'Message sent!', "message": message_body}


@app.get("/check-new-messages/")
async def check_new_messages(
    db_location: str = os.getenv("IMESSAGE_DB_LOCATION"),
    last_rowid: Optional[int] = None,
):
    messages = read_messages(db_location, n=1)
    if messages:
        latest_message = messages[0]
        if last_rowid is None or latest_message["rowid"] > last_rowid:
            return latest_message
    return {"message": "No new messages"}

def print_messages(messages):
    for message in messages:
        sender_receiver = "Me" if message["is_from_me"] else message["phone_number"]
        print(f"{sender_receiver}: {message['body']} ({message['date']})")

if __name__ == "__main__":
    print(get_messages())
