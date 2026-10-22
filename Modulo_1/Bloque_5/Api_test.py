import requests
import json
from dotenv import load_dotenv
import os
# cargar variables de entorno
load_dotenv()
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"

payload = json.dumps({
  "contents": [
    {
      "parts": [
        {
          "text": "explicame como funciona la nba en 20 palabras."
        }
      ]
    }
  ]
})
headers = {
  'Content-Type': 'application/json',
  'x-goog-api-key': os.getenv("GEMINI_API_KEY"),
}

try:

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
except Exception as e:

    print ("error:",e)

    print ("API request completed.")