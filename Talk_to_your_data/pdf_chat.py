import streamlit as st
from chatbot_agent import ChatbotAgent
from tools.pdf_reader3 import pdf_loader
chatbot=ChatbotAgent()
# Clears chat history displayed on the chatbot screen
def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant", "content": "Upload some PDFs and ask me a question"}]

logo = r"message.png"

def main():
    st.set_page_config(
        page_title="Products Query",
        page_icon=logo
    )



    # Sidebar for uploading PDF files and selecting options
    with st.sidebar:
        st.title("Menu:")
        # Uploading files through Streamlit
        pdf_docs = st.file_uploader(
            "Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True,
            type=["pdf", "docx", "txt", 'xlsx', 'csv', "doc"])
        
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                pdf_loader.pdf_reader(pdf_docs)
                if len(pdf_docs) == 0:
                    st.warning("No files uploaded.")
                else:
                    st.success("Done")
        
        # Select output context size as a slider
        # output_context_size = st.slider("Select Output Context Size (in characters)",
        #                                 min_value=100, max_value=6000, step=500,
        #                             )

    # Display the title with embedded logo
    col1, col2 = st.columns([0.2, 1])
    with col1:
        st.image(logo, width=100)
    with col2:
        st.title("Chat bot")
    st.write("Welcome to the chat!")
    
    # Chat input
    # Placeholder for chat messages
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {"role": "assistant", "content": "How may I help you"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    # # Add options for selecting LLM model and temperature
    # llm_model = st.sidebar.selectbox("Select LLM Model", ["GPT-3.5", "GPT-4"])
    # temperature = st.sidebar.slider("Creativity (%)", min_value=10, max_value=100, value=100, step=10, format="%g%%") / 100
    st.sidebar.button('Clear Chat History', on_click=clear_chat_history)
    # chatbot_agent.llm_model(llm_model, temperature, output_context_size)

    # Display chat messages and bot response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response, no_of_characters_used = chatbot.pdf_chat(prompt)
                placeholder = st.empty()
                full_response = ''
                for item in response:
                    full_response += item
                    placeholder.markdown(full_response)
                
                # Concatenate no_of_characters_used to the end of full_response
                # full_response += f"\n\n Number of characters used: {no_of_characters_used}"
                placeholder.markdown(full_response)

        if response is not None:
            message = {"role": "assistant", "content": full_response}
            st.session_state.messages.append(message)
        
if __name__ == "__main__":
    main()




