from Peticiones import make_request
import os
from dotenv import load_dotenv

load_dotenv()


resut = make_request(
   url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent",
   api_key =os.getenv("GEMINI_API_KEY"),
   prompt ="explicame como funciona la nba en 20 palabras."

 )
print(resut["candidates"][0]["content"]["parts"][0]["text"])
