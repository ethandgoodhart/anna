import sqlite3
import datetime
import time
import os
from py_imessage import imessage

def send_imessage(phone_number, message_body):
    os.system('osascript send_imessage.applescript {} "{}"'.format(phone_number, message_body))


def get_chat_mapping(db_location):
    conn = sqlite3.connect(db_location)
    cursor = conn.cursor()

    cursor.execute("SELECT room_name, display_name FROM chat")
    result_set = cursor.fetchall()

    mapping = {room_name: display_name for room_name, display_name in result_set}

    conn.close()

    return mapping


def read_messages(db_location, n=None, self_number='Me', human_readable_date=True):
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
        rowid, date, text, attributed_body, handle_id, is_from_me, cache_roomname = result

        phone_number = self_number if handle_id is None else handle_id

        if text is not None:
            body = text
        elif attributed_body is None: 
            continue
        else: 
            attributed_body = attributed_body.decode('utf-8', errors='replace')
            if "NSNumber" in str(attributed_body):
                attributed_body = str(attributed_body).split("NSNumber")[0]
                if "NSString" in attributed_body:
                    attributed_body = str(attributed_body).split("NSString")[1]
                    if "NSDictionary" in attributed_body:
                        attributed_body = str(attributed_body).split("NSDictionary")[0]
                        attributed_body = attributed_body[6:-12]
                        body = attributed_body

        if human_readable_date:
            date_string = '2001-01-01'
            mod_date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
            unix_timestamp = int(mod_date.timestamp())*1000000000
            new_date = int((date+unix_timestamp)/1000000000)
            date = datetime.datetime.fromtimestamp(new_date).strftime("%Y-%m-%d %H:%M:%S")

        mapping = get_chat_mapping(db_location)

        try:
            mapped_name = mapping[cache_roomname]
        except:
            mapped_name = None

        messages.append(
            {"rowid": rowid, "date": date, "body": body, "phone_number": phone_number, "is_from_me": is_from_me,
             "cache_roomname": cache_roomname, 'group_chat_name': mapped_name})

    conn.close()
    return messages


def print_messages(messages):
    for message in messages:
        sender_receiver = "Me" if message["is_from_me"] else message["phone_number"]
        print(f"{sender_receiver}: {message['body']} ({message['date']})")


def check_new_messages(db_location, interval=5):
    last_rowid = None
    while True:
        messages = read_messages(db_location, n=1)
        if messages:
            latest_message = messages[0]
            if last_rowid is None or latest_message["rowid"] > last_rowid:
                print_messages([latest_message])
                last_rowid = latest_message["rowid"]
        time.sleep(interval)


# ask the user for the location of the database
db_location = "/Users/keval/Library/Messages/chat.db"

# # ask the user for the number of messages to read
# n = input("Enter the number of messages to read: ")

# # Remove the 2 lines below after testing -- they are for testing only
# output = read_messages(db_location, n)
# print_messages(output)
# # Remove the 2 lines above after testing -- they are for testing only

# Start checking for new messages
# check_new_messages(db_location)
send_imessage('4046635506', 'another imessage')