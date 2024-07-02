import streamlit as st
import pandas as pd
from utils.data_engineering import process_atheneum_schema
from utils.variable import Variable
from utils.plot_utils import process_analyses
from utils.thinkcell import call_thinkcell_server


EXCEL_EXTENSIONS = {".csv", ".xlsx", ".xls", ".xlsb", "ods", "xlsm", "xltx", "xltm"}


@st.cache_data
def load_data(uploaded_data_file, **kwargs) -> pd.DataFrame:
    """
    Load a file into a Pandas dataframe. Additional pandas kwargs can be passed.
    Follos the assumption that the data can be found in the first sheet, and the schema is in the second sheet

    Args:
        uploaded_data_file (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        if uploaded_data_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_data_file, **kwargs).fillna("")

        elif uploaded_data_file.name.endswith(tuple(EXCEL_EXTENSIONS - {".csv"})):
            data = pd.read_excel(uploaded_data_file, sheet_name=0)

            for col in data.columns:
                if data[col].dropna().apply(lambda x: pd.api.types.is_float(x) and float.is_integer(x)).all():
                    data[col] = data[col].astype(pd.Int16Dtype())

    except Exception as e:
        print(f"An unexpected error occurred when loading data: {e}")

    else:
        return data#.astype(str)


def on_change_independent_var():
    if st.session_state.independent_dd == st.session_state.dependent_dd:
        st.session_state.pop("dependent_dd")


    else:
        st.session_state.dependent_dd = st.session_state.dependent_dd


@st.cache_data
def extract_keys_from_survey(survey_file):
    schema = process_atheneum_schema(survey_file)
    reverse_key_map_no_metadata = {value["question_text"]: key for key, value in schema.items() if not value["is_metadata"]}

    return schema, reverse_key_map_no_metadata


# Initialise the Page and set up state variables
st.set_page_config(page_title="CHARTER", layout="wide")
if "analysis_reset" not in st.session_state:
    st.session_state.analyis_reset = False


def ind_filter_on_click():
    if "All" in st.session_state.ind_filter_multi_select:
        st.session_state.ind_filter_multi_select = st.session_state.independent_values


def dep_filter_on_click():
    if "All" in st.session_state.dep_filter_multi_select:
        st.session_state.dep_filter_multi_select = st.session_state.dependent_values 


if "annotations" not in st.session_state:
    st.session_state.annotations = []

if "bullet_point" not in st.session_state:
    st.session_state.bullet_point = None


def submit_bullet_point():
    st.session_state.annotations.append(st.session_state.bullet_point)
    st.session_state.pop("bullet_point")


### UI Menu. Wrap the below in a bigger function.
# Shared UI elements
st.title("Charter")
st.subheader("🔍 CHARTER")
st.subheader("Data Interrogation Platform for Management Consultants.\nBegin by uploading your survey data.")

# File upload widgets
st.file_uploader("Upload some survey data", type=EXCEL_EXTENSIONS, key="uploaded_file")
st.header("Analysis")

if st.session_state.uploaded_file is not None:
    # if "data_file" not in st.session_state:
    #     st.session_state.data_file = data_file

    # if data_file != st.session_state.data_file:
    #     st.session_state.data_file = data_file

    # if "question_schema" not in st.session_state:

        

        # field_text_to_key = {}
        # for key, value in schema.items():
        #     field_text = value['field_text']
        #     if field_text not in field_text_to_key:
        #         field_text_to_key[field_text] = []
        #     field_text_to_key[field_text].append(key)

        # st.session_state.field_text_key_map = field_text_to_key
        
    st.session_state.question_schema, st.session_state.dropdown_selections = extract_keys_from_survey(st.session_state.uploaded_file)

    # data = load_data(data_file)
    # uploaded_data_file = client.files.create(file=open(data_file.name, "rb"), purpose="assistants")
    # st.session_state.uploaded_file_ids.append(uploaded_data_file.id)
    # st.session_state.file_uploaded = True
    # st.session_state.columns = data.columns.to_list()

    st.write("The data and schema files have been uploaded and are available for analysis.")
    
    filter_col, plot_col = st.columns([0.25, 0.75], gap="medium")
    with filter_col:
        filter_container = st.container()
        export_container = st.container()

    with plot_col:
        plot_container = st.container()
    
    filter_container.subheader("Settings")

    reset_col, swap_col = filter_container.columns(2)
    with reset_col:
        st.button(
            label="Reset Analysis?",
            key="analysis_reset"
        )

    if st.session_state.analysis_reset:
        st.session_state.pop("independent_dd")
        st.session_state.pop("dependent_dd")   
    
    if "independent_dd" not in st.session_state:
        st.session_state.independent_dd = None

    if "dependent_dd" not in st.session_state:
        st.session_state.dependent_dd = None

    with swap_col:
        st.button(
            "Swap Variables?",
            disabled=st.session_state.dependent_dd is None or st.session_state.independent_dd is None,
            key="data_transpose"
        )

        if st.session_state.data_transpose:
            st.session_state.independent_dd, st.session_state.dependent_dd = st.session_state.dependent_dd, st.session_state.independent_dd
    
    independent_container = filter_container.container()
    dependent_container = filter_container.container()
    
    independent_container.selectbox(
        label="Select your Independent Variable",
        options=list(st.session_state.dropdown_selections.keys()),
        index=None,
        key="independent_dd",
        on_change=on_change_independent_var
    )

    
    # if st.session_state.independent_dd:
    #     independent_variables = load_data(st.session_state.uploaded_file, _usecols=st.session_state.independent_dd)[st.session_state.independent_dd].unique().tolist()
    #     default_filter_values = independent_variables
    #     filter_options = ["All"] + independent_variables
    #     filter_container.multiselect(
    #         label="",
    #         default=default_filter_values,
    #         options=filter_options,
    #         disabled = st.session_state.independent_dd is None,
    #         key="filter_multi_select",
    #         on_change=ind_filter_on_click
    #     )
    
    # else:
    #     filter_options = []
    #     default_filter_values = None

    dependent_container.selectbox(
        "Select an Optional Dependent Variable",
        options=[c for c in st.session_state.dropdown_selections.keys() if c != st.session_state.independent_dd],
        index=None,
        key="dependent_dd",
    )

    plot_container.subheader("Results")
    plot_container.selectbox(
        label="Select Chart Type",
        options=["stack", "100%"],
        index=0,
        key="barchart_type"
    )

    if st.session_state.independent_dd:
        data = load_data(st.session_state.uploaded_file)
        
        independent_id = st.session_state.dropdown_selections[st.session_state.independent_dd]
        if data.loc[:, independent_id].dropna().empty:
            plot_container.warning(f"Independent Variable '{st.session_state.independent_dd}' contains no data.")
            st.session_state.ifilter_disabled = True

        else:
            st.session_state.ifilter_disabled = False

        independent_var = Variable(
            variable_id=independent_id,
            variable_metadata=st.session_state.question_schema[independent_id]
        )

        st.session_state.independent_values = data.loc[:, independent_id].dropna().unique().tolist()
        if independent_var.encodings:
            reverse_i_map = {value: key for key, value in independent_var.encodings.items()}
            st.session_state.independent_values = [independent_var.encodings[str(item)] for item in st.session_state.independent_values]

        else:
            reverse_i_map = None

        independent_container.multiselect(
            label="",
            default=st.session_state.independent_values,
            options=["All"] + st.session_state.independent_values,
            disabled = st.session_state.independent_dd is None or st.session_state.ifilter_disabled,
            key="ind_filter_multi_select",
            on_change=ind_filter_on_click
        )

        if independent_var.is_column and st.session_state.dependent_dd:
            dependent_id = st.session_state.dropdown_selections[st.session_state.dependent_dd]
            independent_id = st.session_state.dropdown_selections[st.session_state.independent_dd]
            if data.loc[:, dependent_id].dropna().empty:
                plot_container.warning(f"Dependent Variable '{st.session_state.dependent_dd}' contains no data.")
                st.session_state.dfilter_disabled = True

            else:
                st.session_state.dfilter_disabled = False

            dependent_var = Variable(
                variable_id=dependent_id,
                variable_metadata=st.session_state.question_schema[dependent_id]
            )

            if not dependent_var.is_column:
                plot_container.warning(f"The multi-select question '{dependent_var.question_text}' is not supported for a dependent variable.")
                dependent_var = None

            st.session_state.dependent_values = data.loc[:, dependent_id].dropna().unique().tolist()
            if dependent_var.encodings:
                reverse_d_map = {value: key for key, value in dependent_var.encodings.items()}
                st.session_state.dependent_values = [dependent_var.encodings[str(item)] for item in st.session_state.dependent_values]

            else:
                reverse_d_map = None

            dependent_container.multiselect(
                label="",
                default=st.session_state.dependent_values,
                options=["All"] + st.session_state.dependent_values,
                disabled = st.session_state.dependent_dd is None or st.session_state.dfilter_disabled,
                key="dep_filter_multi_select",
                on_change=dep_filter_on_click
            )

        elif independent_var.is_column and st.session_state.dependent_dd is None:
            dependent_var = None

        elif not independent_var.is_column:
            if st.session_state.dependent_dd:
                plot_container.warning(f"Independent Variable '{independent_var.question_text}' is a Multi-Select Question. Dependent Variable will be ignored.")

            dependent_var = Variable(
                "values",
                variable_metadata={
                    "question_text": "values",
                    "related_columns": ["values"],
                    "is_column": True,
                    "encodings": independent_var.encodings
                }
            )

            temp_var = independent_var

            independent_var = Variable(
                variable_id=temp_var.variable_id,
                variable_metadata={
                    "question_text": temp_var.question_text,
                    "related_columns": ["rows"],
                    "is_column": True,
                    "encodings": {key: value["row_text"] for key, value in temp_var.rows.items()}
                }
            )

            data = data.loc[:, temp_var.columns].melt(
                var_name="rows",
                value_name="values"
            )

        if dependent_var:
            df = data[
                (data[independent_id].isin([int(reverse_i_map[value]) for value in st.session_state.ind_filter_multi_select])) &
                (data[dependent_id].isin([int(reverse_d_map[value]) for value in st.session_state.dep_filter_multi_select]))
            ]

        else:
            df = data[
                data[independent_id].isin([int(reverse_i_map[value]) for value in st.session_state.ind_filter_multi_select])
            ]

        figure, thinkcell_json, thinkcell_data = process_analyses(
            df=df,
            ivar=independent_var,
            dvar=dependent_var,
            chart_type=st.session_state.barchart_type,
            chart_template=st.secrets.get("BARCHART_TEMPLATE"),
            # annotations=
        )

        if "plotly_figure" not in st.session_state:
            st.session_state.plotly_figure = figure

        else:
            if st.session_state.plotly_figure != figure:
                st.session_state.plotly_figure = figure

        plot_container.text_input(
            label="Input your analyses here.",
            max_chars=50,
            key="bullet_point",
            on_change=submit_bullet_point
        )

        annotation_md = "\n".join("- %s" % x for x in st.session_state.annotations if x is not None)
        plot_container.markdown(annotation_md)

        # plot_container.text_input(
        #     label="Add a title to your plot.",
        #     max_chars=50,
        #     key="chart_title"
        # )

        plot_container.write(st.session_state.plotly_figure)

        if thinkcell_json is not None and thinkcell_data is not None:
            if plot_container.checkbox("Display Pivot data?"):
                plot_container.subheader("Pivot Data")
                plot_container.dataframe(thinkcell_data, use_container_width=True, hide_index=False)
            
            export_container.subheader("Export")

            xl_filename = export_container.text_input(label="Input a filename for your pivot data.", placeholder="charter_pivot_data.csv")
            if not xl_filename:
                xl_filename = "charter_pivot_data.csv"

            export_container.download_button(
                label="Export Pivot Data",
                file_name=xl_filename,
                mime="text/csv",
                data=thinkcell_data.to_csv(index=True, header=True, encoding="utf-8"),
                disabled=not xl_filename.endswith(".csv")
            )

            pptx_filename = export_container.text_input(
                label="Input a filename for your PowerPoint file.",
                placeholder="charter_plot.pptx"
            )
            
            if not pptx_filename:
                pptx_filename = "charter_plot.pptx"

                generate, download = export_container.columns(2)
                with generate:
                    generate_button = st.button("Generate PowerPoint")

                with download:
                    if generate_button:
                        if pptx_filename.endswith(".pptx"):
                            pptx_data = call_thinkcell_server(thinkcell_json)
                            st.download_button(
                                label="Download PowerPoint",
                                file_name=pptx_filename,
                                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                data=pptx_data
                            )
                        else:
                            st.error("Filename must end with .pptx")

else:
    # TODO: Have a function that resets or pops the necessary state vars
    st.write("No files have been uploaded yet.")
    # st.session_state.file_uploaded = False
    if "analysis_reset" in st.session_state:
        st.session_state.pop("analysis_reset")

    if "analysis_button" in st.session_state:
        st.session_state.pop("analysis_button")

    st.session_state.independent_values = []
    st.session_state.ifilter_disabled = True
    st.session_state.dependent_values = []
    st.session_state.dfilter_disabled = True




