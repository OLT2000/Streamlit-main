"""
demo_app.py
"""
import os
import json
import pandas as pd
import streamlit as st
from utils.plot_utils import create_bar_chart, df_to_thinkcell_json
import plotly.express as px
from plotly import graph_objects as go
from openai import OpenAI
from utils.llm_utils import (
    delete_files,
    delete_thread,
    EventHandler,
    moderation_endpoint,
    is_nsfw,
    render_custom_css,
    render_download_files,
    retrieve_messages_from_thread,
    retrieve_assistant_created_files
)
# from utils.azure_utils import get_ppt_template_names, 


# Initialise the OpenAI client, and retrieve the assistant
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="CHARTER")

# Apply custom CSS
render_custom_css()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["LLM", "Analysis"])

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

if "uploaded_file_ids" not in st.session_state:
    st.session_state.uploaded_file_ids = []

@st.cache_data
def load_data(uploaded_data_file, **kwargs):
    try:
        if uploaded_data_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_data_file, **kwargs)

        elif uploaded_data_file.name.endswith(".xlsx"):
            data = pd.read_excel(uploaded_data_file)
        

    # except UnicodeDecodeError:
    #     return load_data(uploaded_data_file=uploaded_data_file, encoding="cp1252")
        
    except Exception as e:
        print(f"An unexpected error occurred when loading data: {e}")

    else:
        return data

@st.cache_data
def load_schema(schema_file):
    try:
        with open(schema_file, "r") as f:
            schema = json.load(f)
    except Exception as e:
        print(f"An unexpected error occurred when loading schema: {e}")
    else:
        return schema

# Shared UI elements
st.title("Charter")
st.subheader("🔍 CHARTER")
st.subheader("Data Interrogation Platform for Management Consultants.\nBegin by uploading your tabular data in CSV format and then ask a query using the textbox below.")

# File upload widgets
data_file = st.file_uploader("Upload some CSV data", type=("csv", "xlsx"))

schema_flag = st.toggle("Use Column Schema?")
schema_file = st.file_uploader("Upload a schema to support your analysis.", type=("json"), disabled=not schema_flag)

if data_file is not None:
    test_url = data_file._file_urls.upload_url
    # print(test_url)
    # with open(test_url, "r") as f:
    #     print(len(f))
    if "data_file" not in st.session_state:
        st.session_state.data_file = data_file
    if data_file != st.session_state.data_file:
        st.session_state.data_file = data_file


    data = load_data(data_file)
    # uploaded_data_file = client.files.create(file=open(data_file.name, "rb"), purpose="assistants")
    # st.session_state.uploaded_file_ids.append(uploaded_data_file.id)
    st.session_state.file_uploaded = True
    st.session_state.columns = data.columns.to_list()

if schema_file is not None:
    if "schema_file" not in st.session_state:
        st.session_state.schema_file = schema_file
    if schema_file != st.session_state.schema_file:
        st.session_state.schema_file = schema_file
    uploaded_schema_file = client.files.create(file=open(schema_file.name, "rb"), purpose="assistants")
    st.session_state.uploaded_file_ids.append(uploaded_schema_file.id)

# if "analysis_reset" not in st.session_state:
#     st.session_state.analysis_reset = False

if page == "LLM":
    pass
    # st.header("LLM Page")

    # if st.session_state.file_uploaded:
    #     prompt_text = f"You are an expert at data analysis using Python.\nUse your skills to answer questions about the survey data stored in the location '/mnt/data/{st.session_state.uploaded_file_ids[-1]}'. Each row constitutes a respondent to the survey and the columns map to individual survey questions.\n"

    #     if schema_file is not None:
    #         json_schema = [{
    #             "column_name": "The name of the column in the dataset.",
    #             "column_description": "The survey question associated with the above column.",
    #             "column_type": "The type of response - one of (quotas, date, radio, text, checkbox). All options are single select except for checkbox.",
    #             "encodings": {
    #                 "code": "Original value used in the survey."
    #             }
    #         }]
    #         schema_prompt_text = f"\nA schema file has also been uploaded to '/mnt/data/{uploaded_schema_file.id}'."
    #         prompt_text += schema_prompt_text

    #     assistant = client.beta.assistants.update(
    #         assistant_id=st.secrets["ASSISTANT_ID"],
    #         tool_resources={
    #             "code_interpreter": {
    #                 "file_ids": st.session_state.uploaded_file_ids
    #             }
    #         }
    #     )

    #     chat_placeholder = "How many rows is my data?"
    #     st.session_state.disabled = False
    # else:
    #     st.session_state.disabled = True
    #     chat_placeholder = "Upload some CSV data to kick things off!"

    # if schema_flag and not schema_file:
    #     st.session_state.disabled = True

    # if st.checkbox("Display raw data?", disabled=not st.session_state.file_uploaded):
    #     st.subheader("Raw Data")
    #     data = load_data(st.session_state.data_file)
    #     st.dataframe(data)

    # text_box = st.empty()
    # qn_btn = st.empty()

    # question = text_box.text_area("Ask a question", disabled=st.session_state.disabled, placeholder=chat_placeholder)
    # if qn_btn.button("Ask Charter"):
    #     text_box.empty()
    #     qn_btn.empty()

    #     if "thread_id" not in st.session_state:
    #         thread = client.beta.threads.create()
    #         st.session_state.thread_id = thread.id

    #     client.beta.threads.update(
    #         thread_id=st.session_state.thread_id,
    #         tool_resources={"code_interpreter": {"file_ids": st.session_state.uploaded_file_ids}}
    #     )

    #     if "text_boxes" not in st.session_state:
    #         st.session_state.text_boxes = []

    #     client.beta.threads.messages.create(
    #         thread_id=st.session_state.thread_id,
    #         role="assistant",
    #         content=prompt_text
    #     )

    #     client.beta.threads.messages.create(
    #         thread_id=st.session_state.thread_id,
    #         role="user",
    #         content=question
    #     )

    #     st.session_state.text_boxes.append(st.empty())
    #     st.session_state.text_boxes[-1].success(f"**> 🤔 User:** {question}")

    #     with client.beta.threads.runs.stream(thread_id=st.session_state.thread_id,
    #                                          assistant_id=assistant.id,
    #                                          tool_choice={"type": "code_interpreter"},
    #                                          event_handler=EventHandler(),
    #                                          temperature=0) as stream:
    #         stream.until_done()
    #         st.toast("Analysis Complete.")

    #     with st.spinner("Preparing the files for download..."):
    #         assistant_messages = retrieve_messages_from_thread(st.session_state.thread_id)
    #         st.session_state.assistant_created_file_ids = retrieve_assistant_created_files(assistant_messages)
    #         st.session_state.download_files, st.session_state.download_file_names = render_download_files(st.session_state.assistant_created_file_ids)

    #     delete_files(st.session_state.assistant_created_file_ids)
    #     delete_thread(st.session_state.thread_id)

elif page == "Analysis":
    st.header("Analysis Page")

    if st.session_state.file_uploaded:
        st.write("The data and schema files have been uploaded and are available for analysis.")
        st.session_state.analysis_reset = st.button(
            label="Reset Analysis?"
        )
        
        # TODO: Look into callback for the buttons
        col = st.selectbox(
            label="Which column would you like to analyse?",
            options=st.session_state.columns
        )

        # agg = st.selectbox(
        #     label="Select an aggregation to use in analysis.",
        #     options=[
        #         "Count",

        #     ]
        # )

        extra_var = st.selectbox(
            "Would you like to add a third variable?",
            options=[
                None
            ] + [c for c in st.session_state.columns if c != col]
        )
        analysis_btn = st.button("Generate Analysis")
        if "analysis_button" not in st.session_state:
            st.session_state.analysis_button = analysis_btn
        
        else:
            st.session_state.analysis_button = not st.session_state.analysis_reset

        if st.session_state.analysis_button:
            df = load_data(data_file)
            count_df = df[col].value_counts().reset_index()

            fig, sub_df = create_bar_chart(df, col, extra_var, barmode="stack")

            tc_json, tc_df = df_to_thinkcell_json(sub_df, col, extra_var)

            if "plotly_figure" not in st.session_state:
                st.session_state.plotly_figure = fig
            
            else:
                if st.session_state.plotly_figure != fig:
                    st.session_state.plotly_figure = fig

            st.plotly_chart(st.session_state.plotly_figure)

            if st.checkbox("Display raw data?"):
                st.subheader("Raw Data")
                st.dataframe(sub_df, use_container_width=True, hide_index=True)

            if st.checkbox("Display Pivot data?"):
                st.subheader("Raw Data")
                st.dataframe(tc_df, use_container_width=True, hide_index=False)

            tc_export, xl_export = st.columns(2)
            with tc_export:
                thinkcell_filename = st.text_input(label="Input a filename for your thinkcell ppttc file.", placeholder="charter_thinkcell.ppttc")
                if not thinkcell_filename:
                    thinkcell_filename = "charter_thinkcell.ppttc"

                st.download_button(
                    label="Export to Think-Cell",
                    file_name=thinkcell_filename,
                    mime="application/json",
                    data=tc_json,
                    disabled=not thinkcell_filename.endswith(".ppttc")
                )
            
            with xl_export:
                xl_filename = st.text_input(label="Input a filename for your pivot data file.", placeholder="charter_data.csv")
                if not xl_filename:
                    xl_filename = "charter_data.csv"

                st.download_button(
                    label="Export to CSV",
                    file_name=xl_filename,
                    mime="text/csv",
                    data=tc_df.to_csv(index=True, header=True, encoding="utf-8"),
                    disabled=not xl_filename.endswith(".csv")
                )

    else:
        st.write("No files have been uploaded yet.")
