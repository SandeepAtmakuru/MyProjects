import os
from langchain.tools import tool
from langchain_community.utilities import BingSearchAPIWrapper
from functools import lru_cache

@lru_cache(maxsize=128)
class SearchTools():
    @tool
    def search_internet(query:str) ->str:
        """Useful to search the internet
        about a a given topic and return relevant results"""
        print("Search is Triggered")
        print(f"Input_Qurery:{query}")
        search = BingSearchAPIWrapper()
        #For search.results() if needed
        # search_result =""
        # for i in result:
        #     search_result+=f"{i['title']}\n\n {i['snippet']}\n\n{i['link']}"
        #     search_result+="\n"
        print("Search is used")
        return search.run(query)