import requests
import json

# DBL API Configuration
DBL_API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0IjoxLCJpZCI6IjEzNzY4NDAzMzI1NzgxMzIwNjkiLCJpYXQiOjE3NDg1Mzg0Mzd9.tJGwMaZAMcTNUGoAG_MzJMtuxgZMyp5HGvB7F4MlBT4"
BOT_ID = "1376840332578132069"  # Your bot's Discord ID

COMMANDS = [
    {
        "name": "reporttrotskyist",
        "description": "Report a Trotskyist and laugh at them.",
        "type": 1,
        "options": [
            {
                "type": 6,
                "name": "user",
                "description": "The Trotskyist to report",
                "required": True
            }
        ]
    },
    {
        "name": "reporttankie",
        "description": "Report a Tankie and laugh at them.",
        "type": 1,
        "options": [
            {
                "type": 6,
                "name": "user",
                "description": "The Tankie to report",
                "required": True
            }
        ]
    },
    {
        "name": "studygroup",
        "description": "Create a temporary study voice channel.",
        "type": 1,
        "options": [
            {
                "type": 3,
                "name": "name",
                "description": "Name of the study group",
                "required": True
            }
        ]
    },
    {
        "name": "randomfigure",
        "description": "Get a random revolutionary figure and short bio.",
        "type": 1
    },
    {
        "name": "reading",
        "description": "Get a recommended socialist or communist text to read.",
        "type": 1
    },
    {
        "name": "quote",
        "description": "Get a random communist quote.",
        "type": 1
    },
    {
        "name": "reactionary",
        "description": "Get a random reactionary reaction.",
        "type": 1
    },
    {
        "name": "setdailyquotes",
        "description": "Set the channel and optional role for daily quotes.",
        "type": 1,
        "options": [
            {
                "type": 7,
                "name": "channel",
                "description": "The channel for daily quotes",
                "required": True
            },
            {
                "type": 8,
                "name": "role",
                "description": "Optional role to mention",
                "required": False
            }
        ]
    },
    {
        "name": "stopdaily",
        "description": "Stop daily quotes in this server.",
        "type": 1
    },
    {
        "name": "fact",
        "description": "Get a random communist or socialist historical fact.",
        "type": 1
    },
    {
        "name": "asklenin",
        "description": "Ask Comrade Lenin a question.",
        "type": 1,
        "options": [
            {
                "type": 3,
                "name": "question",
                "description": "Your question for Lenin",
                "required": True
            }
        ]
    }
]


def post_commands_to_dbl():
    """Send commands to Discord Bot List API"""
    headers = {
        "Authorization": DBL_API_TOKEN,
        "Content-Type": "application/json"
    }
    url = f"https://discordbotlist.com/api/v1/bots/{BOT_ID}/commands"
    
    try:
        response = requests.post(url, headers=headers, json=COMMANDS)
        response.raise_for_status()
        print("✅ Successfully posted commands to DBL!")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to post commands: {str(e)}")
        print(f"Response: {response.text if 'response' in locals() else 'N/A'}")


if __name__ == "__main__":
    post_commands_to_dbl()