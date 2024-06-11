"""
demo_app.py
"""
import os
import json
import pandas as pd
import streamlit as st
from openai import OpenAI
from utils import (
    delete_files,
    delete_thread,
    EventHandler,
    moderation_endpoint,
    is_nsfw,
    # is_not_question,
    render_custom_css,
    render_download_files,
    retrieve_messages_from_thread,
    retrieve_assistant_created_files
    )

# Initialise the OpenAI client, and retrieve the assistant
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
# assistant = client.beta.assistants.retrieve(st.secrets["ASSISTANT_ID"])

st.set_page_config(page_title="CHARTER")

# Apply custom CSS
render_custom_css()

# Initialise session state variables
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

if "assistant_text" not in st.session_state:
    st.session_state.assistant_text = [""]

if "code_input" not in st.session_state:
    st.session_state.code_input = []

if "code_output" not in st.session_state:
    st.session_state.code_output = []

if "disabled" not in st.session_state:
    st.session_state.disabled = False


@st.cache_data
def load_data(uploaded_data_file):
    try:
        data = pd.read_csv(uploaded_data_file)

    except Exception as e:
        print(f"An unexpected error occurred when loading data: {e}")

    else:
        return data

# TODO: Implement functionality to map between multiple files/schema
@st.cache_data
def load_schema(schema_file):
    try:
        with open(schema_file, "r") as f:
            schema = json.load(f)
    
    except Exception as e:
        print(f"An unexpected error occurred when loading schema: {e}")

    else:
        return schema

# UI
st.subheader("🔍 CHARTER")
st.subheader("Data Interrogation Platform for Management Consultants.\nBegin by uploading your tabular data in CSV format and the ask a query using the textbox below.")

if "uploaded_file_ids" not in st.session_state:
    st.session_state.uploaded_file_ids = []

# TODO: Make this robust to uploads not from this dir.
# TODO: Upload intellisurvey xlsx and pre-process automatically.
data_file = st.file_uploader("Upload some CSV data", type=("csv"))
schema_flag = st.toggle("Use Column Schema?")
schema_file = st.file_uploader("Upload a schema to support your analysis.", type=("json"), disabled=not schema_flag)


if data_file is not None:
    uploaded_file_ids = []
    uploaded_data_file = client.files.create(
        file=open(data_file.name, "rb"), purpose="assistants"
    )
    uploaded_file_ids.append(uploaded_data_file.id)
    # st.session_state.uploaded_file_ids.append(uploaded_data_file.id)
    
    if schema_file is not None:
        uploaded_schema_file = client.files.create(
            file=open(schema_file.name, "rb"), purpose="assistants"
        )
        # st.session_state.uploaded_file_ids.append(uploaded_schema_file.id)
        uploaded_file_ids.append(uploaded_schema_file.id)


    assistant = client.beta.assistants.update(
        assistant_id=st.secrets["ASSISTANT_ID"],
        tool_resources={
            "code_interpreter": {
            "file_ids": uploaded_file_ids
                }
            } 
        )
        
    # data = load_data(data_file)
    chat_placeholder = "How many rows is my data?"
    st.session_state.disabled = False
    
else:
    st.session_state.disabled = True
    chat_placeholder = "Upload some CSV data to kick things off!"


if schema_flag and not schema_file:
    st.session_state.disabled = True


if st.checkbox("Display raw data?", disabled=not data_file):
    st.subheader("Raw Data")
    data = load_data(data_file)
    st.dataframe(data)



text_box = st.empty()
qn_btn = st.empty()

question = text_box.text_area("Ask a question", disabled=st.session_state.disabled, placeholder=chat_placeholder)
if qn_btn.button("Ask Charter"):

    text_box.empty()
    qn_btn.empty()

    if moderation_endpoint(question):
        st.warning("Your question has been flagged. Refresh page to try again.")
        st.stop()

    # if is_not_question(question):
    #     st.warning("Please ask a question. Refresh page to try again.")
    #     client.beta.threads.delete(st.session_state.thread_id)
    #     st.stop()

    # Create a new thread
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
        print(st.session_state.thread_id)

    # Update the thread to attach the file
    client.beta.threads.update(
                thread_id=st.session_state.thread_id,
                tool_resources={"code_interpreter": {"file_ids": uploaded_file_ids}}
            )

    if "text_boxes" not in st.session_state:
        st.session_state.text_boxes = []
        
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=question
    )

    st.session_state.text_boxes.append(st.empty())
    st.session_state.text_boxes[-1].success(f"**> 🤔 User:** {question}")

    with client.beta.threads.runs.stream(thread_id=st.session_state.thread_id,
                                          assistant_id=assistant.id,
                                          tool_choice={"type": "code_interpreter"},
                                          event_handler=EventHandler(),
                                          temperature=0) as stream:
        stream.until_done()
        st.toast("Analysis Complete.")

    # Prepare the files for download
    with st.spinner("Preparing the files for download..."):
        # Retrieve the messages by the Assistant from the thread
        assistant_messages = retrieve_messages_from_thread(st.session_state.thread_id)
        # For each assistant message, retrieve the file(s) created by the Assistant
        st.session_state.assistant_created_file_ids = retrieve_assistant_created_files(assistant_messages)
        # Download these files
        st.session_state.download_files, st.session_state.download_file_names = render_download_files(st.session_state.assistant_created_file_ids)

    # Clean-up
    # Delete the file(s) created by the Assistant
    delete_files(st.session_state.assistant_created_file_ids)
    # Delete the thread
    delete_thread(st.session_state.thread_id)
