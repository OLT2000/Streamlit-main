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

from string import Template

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
    # print(uploaded_data_file.)
    # st.session_state.uploaded_file_ids.append(uploaded_data_file.id)

    prompt_text = "You are an expert at data analysis using Python.\n" \
        "Use your skills to answer user questions about the survey data uploaded to '{uploaded_data_file.filename}'. Each row constitutes a respondent to the survey and the columns map to individual survey questions.\n"
    
    # prompt_text = f"I have uploaded my tabular survey data to '{uploaded_data_file.filename}'."
    
    if schema_file is not None:
        uploaded_schema_file = client.files.create(
            file=open(schema_file.name, "rb"), purpose="assistants"
        )
        # st.session_state.uploaded_file_ids.append(uploaded_schema_file.id)
        uploaded_file_ids.append(uploaded_schema_file.id)

        json_schema = [{
                    "column_name": "The name of the column in the dataset.",
                    "column_description": "The survey question associated with the above column.",
                    "column_type": "The type of response - one of (quotas, date, radio, text, checkbox). All options are single select except for checkbox.",
                    "encodings": {
                        "code": "Original value used in the survey."
                    }
                }]

        schema_prompt_text = f"\nA schema file has also been uploaded to '{uploaded_schema_file.filename}'."# with the following format:\n{json.dumps(json_schema, indent=4)}\n\nUse the following guidelines to improve your usage of the schema:\n" \
        #     "- The schema will only be in the form of a JSON array object and contain the 4 above key-value pairs.\n" \
        #     "- When the column type is text, quotas, date or radio, each element of the schema maps to exactly one column in the data set.\n" \
        #     "- When the column type is checkbox, each element in the schema maps to multiple columns in the data set according to the encodings. That is, if the element with column_name 'COLUMN' has the encodings {1: 'value', 2: 'value2', 3: 'value3'}, then the data will have three columns titled 'COLUMN.1', 'COLUMN.2' and 'COLUMN.3'\n" \
        #     "- Please read this schema BEFORE performing any analysis.\n" \
        #     "- Use the schema to further understand the user's question and identify relevant columns based on their description, name and encodings.\n\n"
        
        prompt_text += schema_prompt_text

    # plot_guidelines = "When the user requests a visual analysis, ensure that you ALWAYS follow the Plot Guidelines below.\n\n===Plot Guidelines\n" \
    #     "- Please ensure you use Plotly and only Plotly.\n" \
    #     "- DO NOT USE MATPLOTLIB\n" \
    #     "- Apply a dark theme to all plots so that they match the UI.\n" \
    #     "- Render the plotly figure within the chat so that a user can interact with the data."
    #     # "- Ensure that you replace the usual plotly ```python fig.show()``` with ```python st.plotly_chart(fig, theme='streamlit', use_container_width=True)```"
    # prompt_text += plot_guidelines
    # prompt_text = ""

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

    # if moderation_endpoint(question):
    #     st.warning("Your question has been flagged. Refresh page to try again.")
    #     st.stop()

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

    # TODO: Consider how the template impacts chat history.
    print(prompt_text)
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="assistant",
        content=prompt_text
    )

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
