import plotly.express as px
import pandas as pd
import json
from typing import List, Dict, Any
from numpy import unique


colors = ["#034b6f", "#027ab1", "#00a9f4", "#aae6f0", "#d0d0d0"]


def generate_thinkcell_json(column_data, template_path, ppttc_path, x_column_data=None, selected_x_values=None):
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
    
    # Reverse the color scheme
    reversed_colors = colors[::-1]
    single_column_color = "#034b6f"
    print(column_data, "\n\n")
    print(json.dumps([
                        [{"string": "Category"}] + [{"string": str(row[0])} for row in column_data.values],
                        [None] * (len(column_data) + 1),
                        [{"string": "Count"}] + [
                            {"number": int(row[1]), "fill": single_column_color} for row in column_data.values
                        ]
                    ], indent=4))
    
    table = [
        [
            {type_helper(col): col},
            *[{type_helper(val): val} for val in column_data[col].to_list()]
        ] for col in column_data
    ]
    table.insert(1, [])

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

    # if x_column_data is None:
    #     if selected_x_values:
    #         column_data = column_data[column_data[column_data.columns[0]].isin(selected_x_values)]
    #     chart_data = {
    #         "template": template_path,
    #         "data": [
    #             {
    #                 "name": "Chart1",
    #                 "table": [
    #                     [{"string": "Category"}] + [{"string": str(row[0])} for row in column_data.values],
    #                     [None] * (len(column_data) + 1),
    #                     [{"string": "Count"}] + [
    #                         {"number": int(row[1]), "fill": single_column_color} for row in column_data.values
    #                     ]
    #                 ]
    #             }
    #         ]
    #     }
    # else:
    #     if selected_x_values:
    #         x_column_data = x_column_data[x_column_data[x_column_data.columns[0]].isin(selected_x_values)]
    #         column_data = column_data[column_data[column_data.columns[0]].isin(selected_x_values)]
    #     categories = [{"string": str(x)} for x in x_column_data[x_column_data.columns[0]]]
    #     series = [{"string": str(col)} for col in column_data.columns[1:]]

    #     table_data = []
    #     for i in range(len(series)):
    #         row = [{"string": series[i]["string"]}] + [
    #             {"number": int(column_data.iloc[j, i+1]), "fill": reversed_colors[i % len(reversed_colors)]} for j in range(len(categories))
    #         ]
    #         table_data.append(row)

    #     chart_data = {
    #         "template": template_path,
    #         "data": [
    #             {
    #                 "name": "Chart1",
    #                 "table": [
    #                     [{"string": "Category"}] + categories,
    #                     [None] * (len(categories) + 1),
    #                     *table_data
    #                 ]
    #             }
    #         ]
    #     }

    # json_output = json.dumps([chart_data], indent=4)
    # with open(ppttc_path, 'w') as file:
        # file.write(json_output)
    
    return json.dumps(tc_template, indent=4)


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
 

def create_thinkcell_dicts(x: List[int], y: List[Any], c: List[Any]) -> List[Dict[str, Any]]:
    # Get the unique values in x and c
    unique_x = sorted(set(x))  # Ensure unique x values are sorted for consistent dictionary keys
    unique_c = sorted(set(c))
    
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
                    current_dict.append({type_helper(y_value): y_value, "fill": colors[ci]})
                    # current_dict[f"y_{xi}"] = 
                    break  # Break to avoid redundant checks after finding the match
            else:
                # In case no matching y value is found for the specific (x=xi, c=ci) pair
                # TODO: Add type handling for different string/int nulls
                current_dict.append({"number": 0, "fill": colors[ci]})
                # current_dict["number"] = 0  # Or some other default value
        
        # Add the current dictionary to the result list
        result.append(current_dict)
    
    return result


def plotly_json_to_tc(fig_json):
    data = fig_json["data"]
    layout = fig_json["layout"]

    # Extract plot data
    if len(data) != 1:
        raise ValueError(f"Data element is an array of length {len(data)}")
    
    else:
        data = data.pop()
        colour_code = data["marker"]["color"].tolist()
        xvals = data["x"].tolist()
        unique_x = set(xvals)
        lenx = len(xvals)
        
        yvals = data["y"].tolist()
        leny = len(yvals)

        if lenx < leny:
            # TODO: Consider changing 0/"" depending on col type
            xvals += [0] * (leny - lenx)

        elif leny < lenx:
            yvals += [0] * (lenx - leny)

        x_title = layout["xaxis"]["title"]["text"]
        y_title = layout["yaxis"]["title"]["text"]

        table = [
            [
                {"string": y_title}, *[{type_helper(var): var} for var in set(xvals)]
            ],
            [],
            *create_thinkcell_dicts(xvals, yvals, colour_code)
            # *[
            #     [
            #         {type_helper(c): c},
            #         {type_helper(x): x, "fill": colors[c]},
            #         {type_helper(y): y, "fill": colors[c]}
            #     ]
            #     for x, y, c in zip(xvals, yvals, colour_code)
            # ]
        ]

        # table.insert(1, [])

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

        print(tc_template)

        return json.dumps(tc_template, indent=4)
    

def create_bar_chart(df, primary_var, secondary_var, barmode):
    if secondary_var:
        print("SECONDARY")
        # Case 2: Stacked bar chart
        # Grouping by primary and secondary variable to get counts
        grouped_df = df.groupby([primary_var, secondary_var]).size().reset_index(name='count')
        fig = px.bar(grouped_df, x=primary_var, y='count', color=secondary_var, text='count', color_discrete_sequence=colors)
        
    else:
        # Case 1: Simple bar chart
        # Grouping by primary variable to get counts
        grouped_df = df[primary_var].value_counts().reset_index()
        grouped_df.columns = [primary_var, 'count']
        fig = px.bar(grouped_df, x=primary_var, y='count', text='count')

    fig.update_layout(
        title='Bar Chart',
        xaxis_title=primary_var,
        yaxis_title='Count',
        barmode=barmode,
        # bargap=0.2  # Adjusts the gap between bars
    )

    print(fig.data)
    return fig


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
