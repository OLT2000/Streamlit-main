import plotly.express as px
import pandas as pd
import json
from numpy import unique
from collections import defaultdict
from typing import List, Optional, Union, Dict, Any


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
    "Bain": ['#333333', '#5c5c5c', '#858585', '#2c475a', '#cc0000', '#983b72', '#bc73a0', '#d9abc7', '#640a40', '#bccabb', '#83ac9c', '#4f7866', '#0f4c3d', '#a5bbd2', '#7791a8', '#48647c']
}

"""
Original Bain: ['#cc0000', '#2c475a', '#858585', '#5c5c5c', '#333333', '#d9abc7', '#bc73a0', '#983b72', '#640a40', '#bccabb', '#83ac9c', '#4f7866', '#0f4c3d', '#a5bbd2', '#7791a8', '#48647c', '#2c475a']

Bain: [Guardsman Red, Pickled Bluewood, Gray, Scorpion (Slightly Darker Gray), Mine SHaft (Dark Gray), Blossom, Turkish Rose, Rouge, Pumice, Acapulco, Como, Eden, Rock Blue, Bermuda Gray, Blue Bayoux, ]
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
    for idx, row in enumerate(pivot_table.iloc[::].to_records()):
        row = row.tolist()

        label, *values = row
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

    tc_template = [
        {
            "template": template_path,
            "data": [
                {
                    "name": "Title",
                    "table": [[{"string":"A slide title"}]] 
                },
                thinkcell_chart
            ]
        }
    ]

    # thinkcell_json = json.dumps(tc_template, indent=4)

    return tc_template



def generate_thinkcell_json(column_data, template_path, ppttc_path, x_column_data=None, selected_x_values=None):
    # Reverse the color scheme
    # reversed_colors = colors[::-1]
    single_column_color = "#034b6f"

    if x_column_data is None:
        if selected_x_values:
            column_data = column_data[column_data[column_data.columns[0]].isin(selected_x_values)]
        chart_data = {
            "template": template_path,
            "data": [
                {
                    "name": "Chart1",
                    "table": [
                        [{"string": "Category"}] + [{"string": str(row[0])} for row in column_data.values],
                        [None] * (len(column_data) + 1),
                        [{"string": "Count"}] + [
                            {"number": int(row[1]), "fill": single_column_color} for row in column_data.values
                        ]
                    ]
                }
            ]
        }
    else:
        if selected_x_values:
            x_column_data = x_column_data[x_column_data[x_column_data.columns[0]].isin(selected_x_values)]
            column_data = column_data[column_data[column_data.columns[0]].isin(selected_x_values)]
        categories = [{"string": str(x)} for x in x_column_data[x_column_data.columns[0]]]
        series = [{"string": str(col)} for col in column_data.columns[1:]]

        table_data = []
        for i in range(len(series)):
            row = [{"string": series[i]["string"]}] + [
                {"number": int(column_data.iloc[j, i+1]), "fill": reversed_colors[i % len(reversed_colors)]} for j in range(len(categories))
            ]
            table_data.append(row)

        chart_data = {
            "template": template_path,
            "data": [
                {
                    "name": "Chart1",
                    "table": [
                        [{"string": "Category"}] + categories,
                        [None] * (len(categories) + 1),
                        *table_data
                    ]
                }
            ]
        }

    json_output = json.dumps([chart_data], indent=4)
    with open(ppttc_path, 'w') as file:
        file.write(json_output)


def generate_json_for_thinkcell(data, template_path = "template.pptx"):
    # Convert data to a defaultdict for easier access.
    data = defaultdict(lambda: defaultdict(float), data)

    # Sort years and gather unique sheep types.
    years = sorted(data.keys())
    sheep_types = sorted(set(type for year in data for type in data[year]))

    # Set up the basic structure of the JSON object.
    chart_data = {
        "template": template_path,
        "data": [
            {
                "name": "Chart1",
                "table": [
                    # Header row with year labels.
                    [{"string": "Type"}] + \
                    [{"string": str(year)} for year in years],
                    # Empty row after the header.
                    [{"string": ""}] * (len(years) + 1)
                ] + [
                    # Rows for each sheep type with their data across all years.
                    [{"string": sheep_type}] + [{"number": data[year][sheep_type]}
                                                for year in years]
                    for sheep_type in sheep_types
                ]
            }
        ]
    }

    return json.dumps([chart_data], indent=4)



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
 

def create_thinkcell_dicts(x: List[int], y: List[Any], c: List[Any], l_map, ytitle) -> List[Dict[str, Any]]:
    # Get the unique values in x and c
    unique_x = sorted(set(x))  # Ensure unique x values are sorted for consistent dictionary keys
    unique_c = sorted(set(c), reverse=True) # This should equal lmap.keys()

    # Initialize the result list
    result = []
        
    for ci in unique_c:
        # Create a dictionary for each unique value in c
        current_dict = [{type_helper(ci): ci}]
                
        for xi in unique_x:
            # Find the corresponding y value for each unique x
            for xi_idx, x_val in enumerate(x):
                if x_val == xi and c[xi_idx] == ci:
                    y_value = y[xi_idx]
                    current_dict.append({type_helper(y_value): y_value, "fill": l_map[ci]})
                    # current_dict[f"y_{xi}"] = 
                    break  # Break to avoid redundant checks after finding the match
            else:
                # In case no matching y value is found for the specific (x=xi, c=ci) pair
                # TODO: Add type handling for different string/int nulls
                current_dict.append({"number": 0, "fill": l_map[ci]})
                # current_dict["number"] = 0  # Or some other default value
        
        # Add the current dictionary to the result list
        result.append(current_dict)

    table = [
            [
                {"string": ytitle}, *[{type_helper(var): var} for var in unique_x]
            ],
            [],
            *result
            # *[
            #     [
            #         {type_helper(c): c},
            #         {type_helper(x): x, "fill": colors[c]},
            #         {type_helper(y): y, "fill": colors[c]}
            #     ]
            #     for x, y, c in zip(xvals, yvals, colour_code)
            # ]
        ]
    
    return table


def plotly_json_to_tc(fig_json):
    data = fig_json["data"]
    layout = fig_json["layout"]

    x_title = layout["xaxis"]["title"]["text"]
    y_title = layout["yaxis"]["title"]["text"]

    # print(data)
    # for i, d in enumerate(data):
    #     print("-"*100, i, "-"*100, d, sep="\n")
    # Extract plot data
    if len(data) != 1:
        # raise ValueError(f"Data element is an array of length {len(data)}")
        xvals = []
        yvals = []
        lvals = []
        label_map = dict()

        for d in data:
            c = d["marker"]["color"]
            l = d["name"]
            x = d["x"].tolist()
            y = d["y"].tolist()
            assert len(x) == len(y), f"Number of X vars do not match number of Y vars."

            xvals += x
            yvals += y
            lvals += [l] * len(x)
            label_map[l] = c

        table = create_thinkcell_dicts(xvals, yvals, lvals, label_map, y_title)
        
    else:
        data = data.pop()
        labels = data["marker"]["color"].tolist()
        colour_code = [colors[i] for i in labels]
        label_map = {k: v for k, v in zip(labels, colour_code)}
        xvals = data["x"].tolist()
        print(type(xvals))
        unique_x = set(xvals)
        lenx = len(xvals)
        
        yvals = data["y"].tolist()
        leny = len(yvals)

        if lenx < leny:
            # TODO: Consider changing 0/"" depending on col type
            xvals += [0] * (leny - lenx)

        elif leny < lenx:
            yvals += [0] * (lenx - leny)

        table = create_thinkcell_dicts(xvals, yvals, labels, label_map, y_title)

    tc_template = [
        {
            "template": "template.pptx",
            "data": [
                {
                    "name": "Chart1",
                    "table": table
                }
            ]
        }
    ]

    # print(tc_template)

    return json.dumps(tc_template, indent=4)
    

def create_bar_chart(df, primary_var, secondary_var, barmode):
    # df = df.sort_values(by=[primary_var, secondary_var], ascending=True, inplace=False)
    if secondary_var:
        # Case 2: Stacked bar chart
        # Grouping by primary and secondary variable to get counts
        grouped_df = df.groupby([primary_var, secondary_var]).size().reset_index(name='count').sort_values(by=[primary_var, "count"], ascending=[True, False])

        fig = px.bar(grouped_df, x=primary_var, y='count', color=secondary_var, text='count', color_discrete_sequence=colors)
        
    else:
        # Case 1: Simple bar chart
        # Grouping by primary variable to get counts
        grouped_df = df[primary_var].value_counts().reset_index()
        grouped_df.columns = [primary_var, 'count']
        fig = px.bar(grouped_df, x=primary_var, y='count', text='count', color_discrete_sequence=colors)

    fig.update_layout(
        # title='Bar Chart',
        xaxis_title=primary_var,
        yaxis_title='Count',
        barmode=barmode,
        legend={"traceorder": "reversed"}
        # bargap=0.2  # Adjusts the gap between bars
    )

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
