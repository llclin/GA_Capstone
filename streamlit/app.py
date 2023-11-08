import streamlit as st
from PIL import Image
from llama_index import GPTVectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
import time
from llama_index import StorageContext, load_index_from_storage


st.set_page_config(page_title="Chat assistant for COMPASS", page_icon="🤖", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
st.markdown("<h2 style='text-align: center;'>Chat assistant for Complementarity Assessment Framework (COMPASS) 💼📂📑 </h2>", unsafe_allow_html=True)
st.caption("Disclaimer: This chatbot is an experimental project, the responses generated may be outdated and inaccurate.")
st.caption("Please refer to https://www.mom.gov.sg/passes-and-permits/employment-pass/eligibility for the official details.")

left_co, cent_co,last_co = st.columns(3)
with cent_co:
    image = Image.open('./COMPASS_Overview.png')
    st.image(image, caption='Overview of COMPASS')


if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! I am here to assist you on any questions you might have about COMPASS."},
        {"role": "assistant", "content": "How may I assist you?"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing COMPASS docs – hang tight! This should take 1-2 minutes."):

        storage_context = StorageContext.from_defaults(persist_dir="./improved_index.vecstore")
        
        index = load_index_from_storage(storage_context)
        
        return index

index = load_data()

improved_service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0), 
                                                        context_window=2048, 
                                                        system_prompt = "You are an expert who understands the eligibility criteria of employment pass and your job is to answer questions related to the COMPASS and all relevant requirements. Keep your answers factual and provide more context. When asked about salary criteria or C1, include both the age and sector assumed if not provided before answering.")


#index = load_data()
#chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)
chat_engine = index.as_query_engine(service_context=improved_service_context)


if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking...please be patient with me"):
            response = chat_engine.query(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history
