import streamlit as st
import pandas as pd
import json


@st.cache_data
def load_data(uploaded_data_file, **kwargs):
    try:
        if uploaded_data_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_data_file, **kwargs)

        elif uploaded_data_file.name.endswith(".xlsx"):
            data = pd.read_excel(uploaded_data_file)
        
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