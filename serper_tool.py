import os
import requests
from dotenv import load_dotenv

load_dotenv()

def search_serper(query):
    url = "https://google.serper.dev/search"
    payload = {"q": query}
    headers = {"X-API-KEY": os.getenv("SERPER_API_KEY")}
    response = requests.post(url, json=payload, headers=headers)
    results = response.json()
    snippets = [item.get("snippet", "") for item in results.get("organic", [])]
    return "\n".join(snippets[:5])
