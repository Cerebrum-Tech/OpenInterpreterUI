import datetime as dt
import json

CURRENT_DATE_TIME = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_messages_from_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Assuming the JSON file is named 'system_messages.json' and is in the same directory
file_path = 'system_messages.json'
system_messages = load_messages_from_json(file_path)

# convert the JSON to text
messageString= json.dumps(system_messages)

class PROMPTS:
    system_message = (
        messageString
    )
