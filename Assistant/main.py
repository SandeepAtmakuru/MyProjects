import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import streamlit as st
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
#file path
filePath=os.path.dirname(__file__)
# Function to extract text from a PDF file
def get_pdf_text(pdf):
    text = ""
    pdf_reader = PdfReader(pdf)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to split text into chunks
def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = splitter.split_text(text)
    return chunks  # list of strings

# Function to get embeddings for each chunk and store them in a vector store
def get_vector_store(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")  # type: ignore
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local(os.path.join(filePath,"faiss_index"))

# Function to configure the conversational chain
def get_conversational_chain():
    prompt_template = """
    You are an Assistant for a Data Science professional named Sandeep Atmakuru. Your goal is to answer the questions asked by the user about Sandeep. The details about him will be provided in the context. If you are unable to generate an answer, then respond by saying "I will ask Sandeep about this and will let you know."
    \n\n
    Context:\n {context}?\n
    Question: \n{question}\n
    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", client=genai, temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(llm=model, chain_type="stuff", prompt=prompt)
    return chain

# Function to clear chat history
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": ""}]

# Function to handle user input and generate a response
def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")  # type: ignore
    new_db = FAISS.load_local(os.path.join(filePath,"faiss_index"), embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
    return response

# Main function to run the Streamlit app
def main():
    # Configure page settings
    st.set_page_config(page_title="Assistant", page_icon="🤖", layout="wide")

    # Sidebar for uploading PDF files
    with st.sidebar:
        # st.image("https://example.com/logo.png", width=150)  # Replace with your logo
        st.button('Clear Chat History', on_click=clear_chat_history)

    # Display title and welcome message
    st.title("Sandeep's Assistant 🤖")
    st.markdown("<h4 style='text-align: center;'>Ask anything about Sandeep Atmakuru</h4>", unsafe_allow_html=True)

    # Placeholder for chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Ready to answer your questions"}]

    # Display chat messages in an interactive container
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input("Type your question here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    # Process and display the chatbot's response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = user_input(prompt)
                full_response = response['output_text']
                st.markdown(full_response)
        if response is not None:
            st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Call PDF processing and embedding functions
    raw_text = get_pdf_text(os.path.join(filePath,"Sandeep_Atmakuru.pdf"))
    text_chunks = get_text_chunks(raw_text)
    get_vector_store(text_chunks)

# Run the Streamlit app
if __name__ == "__main__":
    main()
