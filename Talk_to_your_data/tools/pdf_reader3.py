from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
import os
from langchain_community.document_loaders import PyPDFLoader
import tempfile
from langchain.tools import tool
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
CHROMA_PATH = "chat_chroma"
class llmGen:
    apiKey=None
    def setApiKey(key):
        llmGen.apiKey=key
        os.environ['OPENAI_API_KEY']=key

    def getKey(self):
        if self.apiKey:
            return self.apiKey

    def getllm(self):
        llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        streaming=True,
        temperature=0,
        api_key=self.getKey()
        )

        return llm



llm=llmGen()




    



class pdf_loader():
    retrieval_chain=None
    @staticmethod
    def pdf_reader(pdf_files):
        print(pdf_files,type(pdf_files))
        documents=[]
        if pdf_files is None:
            return "I dont have any information"
        for file in pdf_files:
            # Read the content of the uploaded PDF file
            
            # Load the PDF content into PyPDFLoader                  
                if file.name.endswith('.pdf'):
                    content = file.read()
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(content)
                        temp_file_path = temp_file.name
                    try:

                        loader = PyPDFLoader(temp_file_path)
                        documents.extend(loader.load())
                    except Exception as e:
                        print(e)
                elif file.name.endswith(('.docx')) or file.name.endswith(('.doc')):
                    content = file.read()
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(content)
                        temp_file_path = temp_file.name
                    
                    try:
                        loader = Docx2txtLoader(temp_file_path)
                        documents.extend(loader.load())
                    except Exception as e:
                        print(e)
                        return "Say to the user like this: Please upload a proper document"
                
                elif file.name.endswith('.txt'):
                    content = file.read()
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(content)
                        temp_file_path = temp_file.name
                    try:
                        loader = TextLoader(temp_file_path)
                        documents.extend(loader.load())
                    except Exception as e:
                        print(e)
                elif file.name.endswith('.xlsx'):
                    content = file.read()
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(content)
                        temp_file_path = temp_file.name
                    try:
                        loader = UnstructuredExcelLoader(temp_file_path)
                        documents.extend(loader.load())
                    except Exception as e:
                        print(e)
                elif file.name.endswith('.csv'):
                    content = file.read()
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(content)
                        temp_file_path = temp_file.name
                    try:
                        loader = CSVLoader(file_path=temp_file_path, encoding="utf-8", csv_args={
                'delimiter': ','})
                        documents.extend(loader.load())
                    except Exception as e:
                        print(e)
                else:
                    return"Upload a proper format"
                

            
        # Splitting the docs (this part may need adjustment based on the actual splitting mechanism)
        print("Reader running")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        PdfSplits = text_splitter.split_documents(documents)
    
        # Vector store
        try:
            vectorstore = FAISS.from_documents(PdfSplits, embedding=OpenAIEmbeddings(api_key=llm.getKey()))
            # prompt_template = ChatPromptTemplate.from_template("""You are documents QnA chatbot, you will asked to answer some queries, use the vectorstores to answer the queries.Generate proper answers for those queries.<context>{context}</context>.Question:{input}""")
            prompt_template = ChatPromptTemplate.from_template("""You are an documents reader chatbot which helps in answering queries from the uploaded documents.Answer the following question from the vectorstoes.Answer the questions based on the user requirements.Find the most relevent answers from the vectorstores,If the query is not understood, please ask to rephrase it or provide a more elaborate query.If the vectorstoes columns or rows have missing colums or rows generate answers on the avaliable data on the vectorstores.Additionally, please make grammar and spelling corrections here.You are created by  VAST AI - from GDA/DJ Team:

        <context>
        {context}
        </context>

        Question: {input}""")
            print("Reader running")
            # Creating retrieval chain by stuffing the docs 
            document_chain = create_stuff_documents_chain(llm.getllm(), prompt_template)
            retriever = vectorstore.as_retriever()
            pdf_loader.retrieval_chain = create_retrieval_chain(retriever, document_chain)
            print(pdf_loader.retrieval_chain)

        except Exception as e:
            print(e)


        # Prompt defining
        



@tool
def data_reader(query: str) -> str:
    """Helps in searching the uploaded docs for answers. Name is data_reader"""
    print("Reader is Triggerd")
    print(f"Input_Qurery:{query}")
    try:
        response = pdf_loader.retrieval_chain.invoke({"input": query})
    except Exception as e:
        print(e)
        # If an error occurs during retrieval chain invocation, handle it  # Print detailed error information
        return "I dont have any information regarding this try using the search tool to search the internet"
        
    answer = response['answer']
    # print(conversation_history)
    print(answer)
    print("Reader is used")
    return answer
