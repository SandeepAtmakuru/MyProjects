import os
import requests
from langchain.tools import tool
# from functools import lru_cache
import json
from dotenv import load_dotenv
load_dotenv()
# @tool
def internet_search(query: str) -> str:
    """Search the internet to get current information from multiple sources along with links"""
    try:
        result = ""
        response = requests.get("https://customsearch.googleapis.com/customsearch/v1",
                                params={'q': query, 'cx': os.getenv('GoogleCxKey'), 'num': 5, 'key': os.getenv('GoogleSearchAPI')})
        data = response.content.decode('utf-8')
        print(data)
        data = json.loads(data)
        for i in data['items']:
            result += str(i.get("snippet"))
            result += "\n"
            result += str(i.get("link"))
            result += "\n"
            print("Result",result)
        return result
    except Exception as e:
        return f"Error: {str(e)}"
    
