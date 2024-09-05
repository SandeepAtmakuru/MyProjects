from tools.search_tool import internet_search
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools.pdf_reader3 import data_reader
from langchain.globals import set_llm_cache
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from datetime import datetime as dt
from langchain_core.messages import AIMessage, HumanMessage
from langchain.agents import Tool
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents import AgentExecutor, create_openai_tools_agent
from dotenv import load_dotenv
load_dotenv()
from langchain_core.tools import Tool
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.cache import InMemoryCache
from pydantic import BaseModel
class SearchArgs(BaseModel):
    query: str
set_llm_cache(InMemoryCache())
chat_history = []
MEMORY_KEY = "chat_history"
        #Building tools for the agents
# reader_tool =StructuredTool(
#     name="data_reader",
#     description="Use this to search for the data_reader to find answers",
#     func=retrieve
# )

# search_tool =StructuredTool(
#     name="internet_search",
#     description="Use this to search the internet",
#     func=search_internet
# )


#Assigning tools

tools=[data_reader,internet_search]
total_length=0
date = dt.today().date()

# prompt=ChatPromptTemplate.from_messages(
#             [
#                 (
#                     "system",
#                     f"""Your are conversational chatbot that answers people queries on the uploaded files.You will be given an input.You have memory of the chat use it to mantain context. Use the data_reader tool to find answers and show them in a neatly formated way without alterning or reducing the information. If you find the answer but it responded with  "I don't know" or "I don't have real-time information" or any other respone having no relevent answer then use the search_tool to search for answers this the todays date:{date}.When you find answers from SearchTools.search_internet tool them show a short and crisp response.Never say i dont have current information, instead say can you rephrase the question.You output should be relevent to what the user asked for.You are created by  VAST AI - from GDA/DJ Team:.""",
                    
#                 ),
#                 MessagesPlaceholder(variable_name=MEMORY_KEY),
#                 ("user", "{input}"),
#                 MessagesPlaceholder(variable_name="agent_scratchpad"),
#             ]
#         )
class chatbot_agent():
    
    def llm_model(user_selected_model,temperature,output_size,key,docStatus=False):
        # context_size=f"{output_size} charachters"

        
        if user_selected_model=="GPT-3.5":

            llm_model="gpt-3.5-turbo"
            print("3.5")
        elif user_selected_model=="GPT-4":
            llm_model="gpt-4-0125-preview"
            print("4")
        
        llm = ChatOpenAI(model=llm_model, temperature=temperature,max_tokens=(output_size/1.5), max_retries=3,api_key=key)
        print(f"LLm changed to {llm_model}")
        

        llm_with_tools = llm.bind_tools(tools)
        # agent = (
        #     {
        #         "input": lambda x: x["input"],
        #         "agent_scratchpad": lambda x: format_to_openai_tool_messages(
        #             x["intermediate_steps"]
        #         ),
        #         "chat_history": lambda x: x["chat_history"],
        #     }
        #     | prompt
        #     | llm_with_tools
        #     | OpenAIToolsAgentOutputParser()
        # )
        # prompt.format(docStatus)
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
                    If this Status:{docStatus} is true then documents are uploaded else documents are not uploaded; Based on this use the tools like data reader or intersearch.
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
        agent=create_openai_tools_agent(llm,tools,prompt)
        chatbot_agent.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
    def pdf_chat(query):
        global chat_history
        global total_length
        result=chatbot_agent.agent_executor.invoke({"input":query,"chat_history": chat_history})
        chat_history.extend(
        [
            HumanMessage(content=query),
            AIMessage(content=result["output"]),
        ]
    )   
        
        total_length+=len(result["output"])+len(query)
        return result["output"],total_length