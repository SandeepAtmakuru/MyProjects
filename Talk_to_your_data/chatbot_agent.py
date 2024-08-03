from tools.bing_search_tool import SearchTools
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.pdf_reader3 import retrieve
from langchain.globals import set_llm_cache
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from datetime import datetime as dt
from langchain_core.messages import AIMessage, HumanMessage
from langchain.agents import Tool
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.cache import InMemoryCache

set_llm_cache(InMemoryCache())
chat_history = []

MEMORY_KEY = "chat_history"
        #Building tools for the agents
reader_tool = Tool(
    name="data_reader",
    description="Use this to search for the data_reader to find answers",
    func=retrieve,
)

search_tool = Tool(
    name="internet_search",
    description="Use this to search the internet",
    func=SearchTools.search_internet
)


#Assigning tools
tools=[reader_tool,search_tool]
total_length=0
date = dt.today().date()
prompt=ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    "You are a conversational chatbot that take documents from the user data_reader tool process the data you can use the tool and produce  answers for the queries asked by the user."

                    "You have two tools at your disposal data_reader tool and internet_search tool.Use the data_reader tool to answer quries from the uploaded documents.Use the Internet_search tool to search for general queries asked user."

                    "Always rely on tools for getting the answers.Do not assume anything."
                    "If the tool replies by saying `Could you please provide more details ` or any other response stating it need more information then generate response by asking the user the required information for further processing."
                    "**Important Note**: 
                While giving input to the data_reader tool always give a elaborated  query specifing requirements memory to maintain context."
                    "If you do not know the answer,Never say no or I dont know as an answer.Ask the user to rephrase the query.If the same question is asked then use this text No_reponse_text:`Sorry, I am unable give a response for this query right now.`"

                    "The user can ask you to compare two documents or products in the same document or two products or values for different documents, then gather information of all the products requested by the user using the tools make the comparision and generate response."

                    "You have memory chat_history use it to maintain context."
                    "If the same query is present asked again and its present in the mermory then give answer using the memory but maintain context to see for what particular product the query is asked"

                    "Never give incomplete answers.If the user choose a lower context window then ask him to increase the context window as per your requirement."

                    "You are created by  VAST AI - from GDA/DJ Team".
                    """,
                    
                ),
                MessagesPlaceholder(variable_name=MEMORY_KEY),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

class ChatbotAgent:
    def __init__(self):
        self.chat_history = []
        self.total_length = 0

        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1, max_retries=3)
        llm_with_tools = llm.bind_tools(tools)
        
        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
                "chat_history": lambda x: x["chat_history"],
            }
            | prompt
            | llm_with_tools
            | OpenAIToolsAgentOutputParser()
        )
        
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
    def pdf_chat(self, query):
        result = self.agent_executor.invoke({"input": query, "chat_history": self.chat_history})
        self.chat_history.extend([
            HumanMessage(content=query),
            AIMessage(content=result["output"]),
        ])
        
        self.total_length += len(result["output"]) + len(query)
        return result["output"], self.total_length


