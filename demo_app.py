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
from io import BytesIO
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
from utils.thinkcell import call_thinkcell_server


# Initialise the OpenAI client, and retrieve the assistant
# client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="CHARTER", layout="wide")

# Apply custom CSS
# render_custom_css()

# Sidebar for navigation
# st.sidebar.title("Navigation")
# page = st.sidebar.selectbox("Choose a page", ["LLM", "Analysis"])

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

st.session_state.run_thinkcell = False

if "uploaded_file_ids" not in st.session_state:
    st.session_state.uploaded_file_ids = []

EXCEL_EXTENSIONS = {".csv", ".xlsx", ".xls", ".xlsb", "ods", "xlsm", "xltx", "xltm"}

# TODO[DONE]: Force types to all be object or string
@st.cache_data
def load_data(uploaded_data_file, **kwargs):
    try:
        if uploaded_data_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_data_file, **kwargs).astype(str)

        elif uploaded_data_file.name.endswith(tuple(EXCEL_EXTENSIONS - {".csv"})):
            data = pd.read_excel(uploaded_data_file, sheet_name=0).astype(str)

            
        

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
    

def on_change_independent_var():
    if st.session_state.independent_dd == st.session_state.dependent_dd:
        st.session_state.pop("dependent_dd")

    else:
        st.session_state.dependent_dd = st.session_state.dependent_dd

# Shared UI elements
st.title("Charter")
st.subheader("🔍 CHARTER")
st.subheader("Data Interrogation Platform for Management Consultants.\nBegin by uploading your tabular data in CSV format and then ask a query using the textbox below.")

# File upload widgets
# TODO: Look into using keys here instead of the variable
data_file = st.file_uploader("Upload some CSV data", type=EXCEL_EXTENSIONS)

# schema_flag = st.toggle("Use Column Schema?")
# schema_file = st.file_uploader("Upload a schema to support your analysis.", type=("json"), disabled=not schema_flag)

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

else:
    # TODO: Have a function that resets or pops the necessary state vars
    st.session_state.file_uploaded = False
    if "analysis_reset" in st.session_state:
        st.session_state.pop("analysis_reset")

    if "analysis_button" in st.session_state:
        st.session_state.pop("analysis_button")

st.header("Analysis Page")

if st.session_state.file_uploaded:
    st.write("The data and schema files have been uploaded and are available for analysis.")
    filter_col, plot_col, export_col = st.columns([0.25, 0.5, 0.25], gap="medium")
    with filter_col:
        st.subheader("Settings")
        # Set Up
        # TODO: Consider doing this at the start of loading the page
        

        reset_col, swap_col = st.columns(2)
        with reset_col:
            analysis_reset = st.button(
                label="Reset Analysis?",
            )

        if analysis_reset:
            st.session_state.pop("independent_dd")
            st.session_state.pop("dependent_dd")   
        
        if "independent_dd" not in st.session_state:
            st.session_state.independent_dd = None

        if "dependent_dd" not in st.session_state:
            st.session_state.dependent_dd = None

        with swap_col:
            data_transpose = st.button(
                "Swap Variables?"
            )

        if data_transpose:
            st.session_state.independent_dd, st.session_state.dependent_dd = st.session_state.dependent_dd, st.session_state.independent_dd
        
        st.selectbox(
            label="Select your Independent Variable",
            options=st.session_state.columns,
            index=None,
            key="independent_dd",
            on_change=on_change_independent_var
        )

        if st.session_state.independent_dd:
            independent_variables = load_data(data_file, _usecols=st.session_state.independent_dd)[st.session_state.independent_dd].unique().tolist()
            default_filter_values = independent_variables
            filter_options = ["All"] + independent_variables
        
        else:
            filter_options = []
            default_filter_values = None
            

        # # Research the best way to store DFs when calling them so often.
        # def multi_select_all():
        #     if "All" in st.session_state.filter_multi_select:
        #         st.session_state.filter_multi_select = independent_variables
        
        # st.text("Select Filter Value")
        # select_container = st.container(height=300)
        
        # with select_container:
        #     st.multiselect(
        #         label="",
        #         default=default_filter_values,
        #         options=filter_options,
        #         disabled = st.session_state.independent_dd is None,
        #         key="filter_multi_select",
        #         on_change=multi_select_all
        #     )

        st.selectbox(
            "Select an Optional Dependent Variable",
            options=[c for c in st.session_state.columns if c != st.session_state.independent_dd],
            index=None,
            key="dependent_dd"
        )

    with plot_col:
        st.subheader("Results")
        if st.session_state.independent_dd: # and st.session_state.filter_multi_select != []:
            df = load_data(data_file)
            count_df = df[st.session_state.independent_dd].value_counts().reset_index()

            fig, sub_df = create_bar_chart(
                df=df,
                primary_var=st.session_state.independent_dd,
                secondary_var=st.session_state.dependent_dd,
                primary_values=independent_variables,
                barmode="stack"
            )

            tc_json, tc_df = df_to_thinkcell_json(sub_df, st.session_state.independent_dd, st.secrets.get("BARCHART_TEMPLATE"), st.session_state.dependent_dd)

            if "plotly_figure" not in st.session_state:
                st.session_state.plotly_figure = fig
            
            else:
                if st.session_state.plotly_figure != fig:
                    st.session_state.plotly_figure = fig

            st.plotly_chart(st.session_state.plotly_figure)

            if st.checkbox("Display Pivot data?"):
                st.subheader("Pivot Data")
                st.dataframe(tc_df, use_container_width=True, hide_index=False)

            
        else:
            st.write("Please choose an independent variable to start your analysis.")
    
    with export_col:
        st.subheader("Exports")
        if st.session_state.independent_dd: # and st.session_state.filter_multi_select != []:
            xl_filename = st.text_input(label="Input a filename for your pivot data.", placeholder="charter_pivot_data.csv")
            if not xl_filename:
                xl_filename = "charter_pivot_data.csv"

            st.download_button(
                label="Export Pivot Data",
                file_name=xl_filename,
                mime="text/csv",
                data=tc_df.to_csv(index=True, header=True, encoding="utf-8"),
                disabled=not xl_filename.endswith(".csv")
            )

            # def download_ppt_on_click(html_response)

            pptx_filename = st.text_input(
                label="Input a filename for your PowerPoint file.",
                placeholder="charter_plot.pptx"
            )
            
            if not pptx_filename:
                pptx_filename = "charter_plot.pptx"

            # st.download_button(
            #     label="Generate and Download PPTX",
            #     file_name=pptx_filename,
            #     mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            #     data=call_thinkcell_server(tc_json) if st.session_state.run_thinkcell else None,
            #     disabled=not pptx_filename.endswith(".pptx")
            # )

            generate, download = st.columns(2)
            with generate:
                generate_button = st.button("Generate PowerPoint")
                

            with download:
                if generate_button:
                    if pptx_filename.endswith(".pptx"):
                        pptx_data = call_thinkcell_server(tc_json)
                        st.download_button(
                            label="Download PowerPoint",
                            file_name=pptx_filename,
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            data=pptx_data
                        )
                    else:
                        st.error("Filename must end with .pptx")

else:
    st.write("No files have been uploaded yet.")
