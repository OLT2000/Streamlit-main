import streamlit as st
import pandas as pd
import json

EXCEL_EXTENSIONS = {".csv", ".xlsx", ".xls", ".xlsb", "ods", "xlsm", "xltx", "xltm"}


@st.cache_data
def load_data(uploaded_data_file, **kwargs):
    """
    Load a file into a Pandas dataframe. Additional pandas kwargs can be passed.

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
        return data.astype(str)



@st.cache_data
def load_schema(schema_file):
    try:
        with open(schema_file, "r") as f:
            schema = json.load(f)
    except Exception as e:
        print(f"An unexpected error occurred when loading schema: {e}")
    else:
        return schema