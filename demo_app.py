"""
demo_app.py
"""
import os
import json
import pandas as pd
import streamlit as st
from utils.plot_utils import create_bar_chart, df_to_thinkcell_json, create_bar_plot
import plotly.express as px
from plotly import graph_objects as go
from openai import OpenAI
from io import BytesIO
from utils.data_engineering import process_atheneum_schema
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
from utils.variable import Variable




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
            data = pd.read_csv(uploaded_data_file, **kwargs).fillna("").astype(str)

        elif uploaded_data_file.name.endswith(tuple(EXCEL_EXTENSIONS - {".csv"})):
            data = pd.read_excel(uploaded_data_file, sheet_name=0)#.astype(str)

            for col in data.columns:
                if data[col].dropna().apply(lambda x: pd.api.types.is_float(x) and float.is_integer(x)).all():
                    data[col] = data[col].astype(pd.Int16Dtype())

            data = data.astype(str)

            # for col in data.columns:
            #     if data[col].dropna().apply(lambda x: pd.api.types.is_integer(x)).all():
            #         print(col)

    # except UnicodeDecodeError:
    #     return load_data(uploaded_data_file=uploaded_data_file, encoding="cp1252")
        
    except Exception as e:
        print(f"An unexpected error occurred when loading data: {e}")

    else:
        return data


# def parse_question_schema(excel_sheet)


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
    # BUG: If I remove the independent variable and then 
    if st.session_state.independent_dd == st.session_state.dependent_dd:
        st.session_state.pop("dependent_dd")

    # elif st.session_state.independent_dd is None:
    #     st.session_state.pop("dependent_dd")

    else:
        st.session_state.dependent_dd = st.session_state.dependent_dd


# Shared UI elements
st.title("Charter")
st.subheader("🔍 CHARTER")
st.subheader("Data Interrogation Platform for Management Consultants.\nBegin by uploading your tabular data in CSV format and then ask a query using the textbox below.")

# File upload widgets
# TODO: Look into using keys here instead of the variable
data_file = st.file_uploader("Upload some survey data", type=EXCEL_EXTENSIONS)

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

    if "question_schema" not in st.session_state:

        schema = process_atheneum_schema(data_file)
        reverse_key_map_no_metadata = {value["question_text"]: key for key, value in schema.items() if not value["is_metadata"]}

        # field_text_to_key = {}
        # for key, value in schema.items():
        #     field_text = value['field_text']
        #     if field_text not in field_text_to_key:
        #         field_text_to_key[field_text] = []
        #     field_text_to_key[field_text].append(key)

        # st.session_state.field_text_key_map = field_text_to_key
        st.session_state.question_schema = schema
        st.session_state.dropdown_selections = reverse_key_map_no_metadata

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
                "Swap Variables?",
                disabled=st.session_state.dependent_dd is None or st.session_state.independent_dd is None
            )

        if data_transpose:
            st.session_state.independent_dd, st.session_state.dependent_dd = st.session_state.dependent_dd, st.session_state.independent_dd
        
        st.selectbox(
            label="Select your Independent Variable",
            options=list(st.session_state.dropdown_selections.keys()),
            index=None,
            key="independent_dd",
            on_change=on_change_independent_var
        )

        # if st.session_state.independent_dd:
        #     independent_variables = load_data(data_file, _usecols=st.session_state.independent_dd)[st.session_state.independent_dd].unique().tolist()
        #     default_filter_values = independent_variables
        #     filter_options = ["All"] + independent_variables
        
        # else:
        #     filter_options = []
        #     default_filter_values = None

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
            options=[c for c in st.session_state.dropdown_selections.keys() if c != st.session_state.independent_dd],
            index=None,
            key="dependent_dd",
        )

        # st.selectbox(
        #     label="Select a Question to Analyse.",
        #     options=st.session_state.dropdown_selections,
        #     index=None,
        #     key="question_selection"
        # )

        # if st.session_state.question_selection:
        #     field_codes = st.session_state.field_text_key_map[st.session_state.question_selection]
        #     if not len(field_codes) == 1:
        #         st.warning(f"Available Codes: {field_codes}")

        #     else:
        #         selected_field = field_codes[0]
        #         selected_schema = st.session_state.question_schema[selected_field]
        #         if selected_schema["question_type"] == "table":
        #             sub_fields = [r["sub_field"] for r in selected_schema["rows"]]
        #             sub_field_disabled = False

        #         else:
        #             sub_fields = []
        #             sub_field_disabled = True

        # else:
        #     sub_fields = []
        #     sub_field_disabled = True      

        
        # st.selectbox(
        #     "Select a sub-topic to analyse.",
        #     options=sub_fields,
        #     index=None,
        #     disabled=sub_field_disabled,
        #     key="question_sub_field"
        # )

            

    with plot_col:
        st.subheader("Results")
        st.selectbox(
            label="Select Chart Type",
            options=["stack", "100%"],
            index=0,
            key="barchart_type"
        )
        if st.session_state.independent_dd: # and st.session_state.filter_multi_select != []:
            df = load_data(data_file)
            print(df.columns)

            # count_df = df[st.session_state.independent_dd].value_counts().reset_index()
            # TODO: Turn into a class so we can feed one variable to the function
            independent_id = st.session_state.dropdown_selections[st.session_state.independent_dd]
            independent_var = Variable(
                variable_id=independent_id,
                variable_metadata=st.session_state.question_schema[independent_id]
            )

            # independent_table_key = 
            # independent_table = 
            # independent_variable = independent_table["related_columns"][0]
            # independent_mappings = independent_table["encodings"]

            # TODO: Move the variable assignment to the dropdowns column, so the warning locations are better.
            if st.session_state.dependent_dd:
                dependent_id = st.session_state.dropdown_selections[st.session_state.dependent_dd]
                dependent_var = Variable(
                    variable_id=dependent_id,
                    variable_metadata=st.session_state.question_schema[dependent_id]
                )
            
            else:
                dependent_var = None

            if not independent_var.is_column:
                if dependent_var:
                    st.warning("Independent Variable is a Multi-Select Question. Dependent Variable will be ignored.")


            #     dep_table_key = 
            #     dep_table = st.session_state.question_schema[dep_table_key]
            #     dep_variable = dep_table["related_columns"][0]
            #     dep_mappings = dep_table["encodings"]

            # else:
            #     dep_variable = None

            # fig, sub_df = create_bar_chart(
            #     df=df,
            #     primary_var=independent_variable,
            #     secondary_var=dep_variable,
            #     primary_values=None,#independent_variables,
            #     barmode="stack",
            #     mappings=independent_mappings
            # )

            fig, sub_df, ind_col, dep_col = create_bar_plot(
                df=df,
                ivar=independent_var,
                dvar=dependent_var,
                chart_type=st.session_state.barchart_type
            )

            if "plotly_figure" not in st.session_state:
                st.session_state.plotly_figure = fig

            else:
                if st.session_state.plotly_figure != fig:
                    st.session_state.plotly_figure = fig

            st.plotly_chart(st.session_state.plotly_figure)

            tc_json, tc_df = df_to_thinkcell_json(sub_df, ind_col, st.secrets.get("BARCHART_TEMPLATE"), dep_col)
            
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
