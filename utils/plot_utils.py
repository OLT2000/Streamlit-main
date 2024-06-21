import plotly.express as px
import pandas as pd
import json
from numpy import unique
from collections import defaultdict
from typing import List, Optional, Union, Dict, Any
from streamlit import warning


def transform_to_pivot(data: pd.DataFrame, primary_col: str, secondary_col: Optional[str] = None) -> pd.DataFrame:
    if secondary_col:
        # Two-variable analysis
        pivot_table = data.pivot(index=secondary_col, columns=primary_col, values='count').fillna(0)
    else:
        # One-variable analysis
        pivot_table = data.pivot_table(index=['count'], columns=primary_col, aggfunc='size')
    
    # Reset index to ensure the index is not multi-index and columns are well-formatted
    # pivot_table = pivot_table.reset_index().rename_axis(None, axis=1)
    
    return pivot_table


colour_mappings = {
    "McKinsey": ["#034b6f", "#027ab1", "#00a9f4", "#aae6f0", "#d0d0d0"],
    "Bain": ['#333333', '#5c5c5c', '#858585', '#2c475a', '#cc0000', '#983b72', '#bc73a0', '#d9abc7' , '#b4b4b4', '#640a40', '#bccabb', '#83ac9c', '#4f7866', '#0f4c3d', '#a5bbd2', '#7791a8', '#48647c', '#46647c', '#2e475b', '#FF0000', '#CD5C5C', '#F08080', '#FA8072', '#E9967A', '#FFA07A', '#DC143C', '#B22222', '#8B0000', '#DCDCDC', '#D3D3D3', '#C0C0C0', '#A9A9A9', '#696969', '#778899', '#708090', '#2F4F4F', '#FFA500', '#FFA07A', '#FF7F50', '#FF6347', '#FF4500', '#FF8C00']
}

"""
Original Bain: ['#cc0000', '#2c475a', '#858585', '#5c5c5c', '#333333', '#d9abc7', '#bc73a0', '#983b72', '#640a40', '#bccabb', '#83ac9c', '#4f7866', '#0f4c3d', '#a5bbd2', '#7791a8', '#48647c', '#2c475a', ]

Bain: [Guardsman Red, Pickled Bluewood, Gray, Scorpion (Slightly Darker Gray), Mine SHaft (Dark Gray), Blossom, Turkish Rose, Rouge, Pumice, Acapulco, Como, Eden, Rock Blue, Bermuda Gray, Blue Bayoux, ]

Bain v2 #e9cd48 #c6aa3c #ac8830 #d9abc7 #b974a1 #963b74 #640a40 #bccabb #82ab9b #4f7866 #0e4c3d #a5bbd2 #7791aa #46647c #2e475b
"""

current_selection = "Bain"

colors = colour_mappings[current_selection]

def df_to_thinkcell_json(data: pd.DataFrame, primary_col: str, template_path: str, secondary_col: Optional[str]) -> str | Dict:
    if secondary_col:
        pivot_table = data.pivot(columns=primary_col, index=secondary_col).fillna(0)
        fill_colours = colors

    else:
        pivot_table = data.set_index(primary_col).T
        fill_colours = [colors[0]]

    pivot_table.sort_values(by=pivot_table.columns[0], ascending=False, inplace=True)

    init_row_tc = [
        {type_helper(primary_col): primary_col},
        *[
            {type_helper(i): i} for i in pivot_table.columns.get_level_values(primary_col).values.tolist()
        ]
    ]

    thinkcell_table_data = []
    if len(pivot_table) > len(fill_colours):
        warning("Run Out Of Colours To Choose From. Defaulting to Grey.")
        # raise IndexError("More variables than colours available")
    
    for idx, row in enumerate(pivot_table.iloc[::].to_records()):
        row = row.tolist()

        label, *values = row

        if idx >= len(fill_colours):
            colour = "#A3A3A3"
        else:
            colour = fill_colours[idx]
        tc_row = [
            {type_helper(label): label},
            *[
                {type_helper(el): el, "fill": colour} for el in values
            ]
        ]

        thinkcell_table_data.append(tc_row)

    thinkcell_chart = {
        "name": "BarChart",
        "table": [
            init_row_tc, [], *thinkcell_table_data[::-1]
        ]
    }

    if secondary_col:
        chart_title = secondary_col

    else:
        chart_title = primary_col

    tc_template = [
        {
            "template": template_path,
            "data": [
                {
                    "name": "BarChartTitle",
                    "table": [[{"string":chart_title}]] 
                },
                thinkcell_chart
            ]
        }
    ]

    # thinkcell_json = json.dumps(tc_template, indent=4)

    return tc_template, pivot_table


def type_helper(variable):
        var = type(variable)
        if pd.api.types.is_string_dtype(var):
            return "string"
        
        elif pd.api.types.is_numeric_dtype(var):
            return "number"
        
        elif pd.api.types.is_datetime64_dtype(var):
            return "datetime"
        
        else:
            raise TypeError(f"Cannot determine appropriate dtype of {var}.\nVariable is of type {type(var)}")
 

def create_bar_chart(df, primary_var, secondary_var, primary_values, barmode):
    # df = df.sort_values(by=[primary_var, secondary_var], ascending=True, inplace=False)
    if secondary_var:
        # Case 2: Stacked bar chart
        # Grouping by primary and secondary variable to get counts
        grouped_df = df.loc[df[primary_var].isin(primary_values)].groupby([primary_var, secondary_var]).size().reset_index(name='count').sort_values(by=[primary_var, "count"], ascending=[True, False])

        fig = px.bar(grouped_df, x=primary_var, y='count', color=secondary_var, text='count', color_discrete_sequence=colors)
        
    else:
        # Case 1: Simple bar chart
        # Grouping by primary variable to get counts
        grouped_df = df.loc[df[primary_var].isin(primary_values)][primary_var].value_counts().reset_index()
        grouped_df.columns = [primary_var, 'count']
        fig = px.bar(grouped_df, x=primary_var, y='count', text='count', color_discrete_sequence=colors)

    fig.update_layout(
        # title='Bar Chart',
        xaxis_title=primary_var,
        yaxis_title='Count',
        barmode=barmode,
        legend=dict(
            orientation="h",
            entrywidth=0.0,
            entrywidthmode="pixels",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
    )

    # fig.update_xaxes(type="category")
    fig.update_traces(textangle=0)

    # print(fig.data)
    return fig, grouped_df


if __name__ == "__main__":
    # Example usage:
    # Assuming df is your DataFrame and you have columns 'gender' and 'income'

    # Example DataFrame
    data = {
        'gender': ['0', '1', '0', '1', '1', '0'],
        'income': ['Low', 'Medium', 'High', 'Medium', 'Low', 'High']
    }

    df = pd.DataFrame(data)

    # Test the function with example DataFrame
    fig = create_bar_chart(df, 'gender', 'income', "group")
    fig.show()
