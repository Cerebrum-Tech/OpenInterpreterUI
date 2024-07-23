import datetime as dt
import json

CURRENT_DATE_TIME = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class PROMPTS:

    def __init__(self, json_file):
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
                
                # Debugging: Print the data to ensure it's read correctly
                print("Loaded data:", data)
                
                if isinstance(data, dict) and "system_message" in data:
                    self.system_message = "\n".join(data["system_message"]) + f"\nToday is {CURRENT_DATE_TIME}.\n"
                else:
                    raise ValueError("JSON structure is not as expected. 'system_message' key not found or data is not a dictionary.")
                    
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

# Example usage:
prompts = PROMPTS('./prompts.json')
print(prompts.system_message)

