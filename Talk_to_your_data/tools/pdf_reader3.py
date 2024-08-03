from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredExcelLoader, CSVLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.tools import tool
from dotenv import load_dotenv
import tempfile
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI API key
key = os.getenv("OPENAI_API_KEY")

# Initialize the language model
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    streaming=True,
    temperature=0
)

class PDFLoader:
    @staticmethod
    def pdf_reader(pdf_files):
        documents = []
        if pdf_files is None:
            return "No files provided."

        for file in pdf_files:
            content = file.read()
            temp_file_path = tempfile.mktemp()

            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(content)

            try:
                if file.name.endswith('.pdf'):
                    loader = PyPDFLoader(temp_file_path)
                elif file.name.endswith(('.docx', '.doc')):
                    loader = Docx2txtLoader(temp_file_path)
                elif file.name.endswith('.txt'):
                    loader = TextLoader(temp_file_path)
                elif file.name.endswith('.xlsx'):
                    loader = UnstructuredExcelLoader(temp_file_path)
                elif file.name.endswith('.csv'):
                    loader = CSVLoader(file_path=temp_file_path, encoding="utf-8", csv_args={'delimiter': ','})
                else:
                    return "Unsupported file format."

                documents.extend(loader.load())
            except Exception as e:
                print(f"Error loading {file.name}: {e}")

        # Split the documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)

        try:
            # Create FAISS vector store
            vectorstore = FAISS.from_documents(splits, embedding=OpenAIEmbeddings())
            prompt_template = ChatPromptTemplate.from_template("""You are a document reader chatbot. Answer the following questions based on the uploaded documents. If the query is unclear or the data is insufficient, ask the user to provide more details or clarify the query.

            <context>
            {context}
            </context>

            Question: {input}""")

            # Create retrieval chain
            document_chain = create_stuff_documents_chain(llm, prompt_template)
            retriever = vectorstore.as_retriever()
            PDFLoader.retrieval_chain = create_retrieval_chain(retriever, document_chain)
        except Exception as e:
            print(f"Error creating retrieval chain: {e}")

@tool
def retrieve(query: str) -> str:
    """Searches the documents for answers"""
    print(f"Query: {query}")
    try:
        response = PDFLoader.retrieval_chain.invoke({"input": query})
        answer = response['answer']
    except Exception as e:
        print(f"Error retrieving answer: {e}")
        return "No information available. Please try rephrasing your query."

    print(f"Answer: {answer}")
    return answer
