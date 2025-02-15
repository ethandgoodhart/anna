# iMessage Integration

This project provides a Python-based integration for sending and reading iMessages on macOS. It uses the `py-imessage` library and AppleScript to interact with the Messages app.

## Requirements

- macOS
- Python 3.11 or higher
- `poetry` for dependency management

## Setup

1. **Clone the repository:**

   ```sh
   git clone <repository-url>
   cd iMessageIntegration
   ```

2. **Install dependencies:**

   ```sh
   poetry install
   ```

3. **Configure the database location:**

   Update the `db_location` variable in iMessage.py to point to your Messages database. The default location is:

   ```py
   db_location = "/Users/<your-username>/Library/Messages/chat.db"
   ```

## Usage

### Sending an iMessage

To send an iMessage, you can use the `send_imessage` function. This function uses an AppleScript to send the message.

Example usage:

```py
from iMessage import send_imessage

send_imessage('1234567890', 'Hello, this is a test message!')
```

### Reading Messages

You can read messages from the Messages database using the `read_messages` function. This function returns a list of messages with details such as the sender, message body, and timestamp.

Example usage:

```py
from iMessage import read_messages, print_messages

messages = read_messages(db_location, n=10)
print_messages(messages)
```

### Checking for New Messages

To continuously check for new messages, you can use the `check_new_messages` function. This function will print new messages as they arrive.

Example usage:

```py
from iMessage import check_new_messages

check_new_messages(db_location, interval=5)
```

## AppleScript

The AppleScript used for sending iMessages is located in send_imessage.applescript. This script is called by the `send_imessage` function in Python.

## License

This project is licensed under the MIT License.
