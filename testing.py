import plotly.express as px
import pandas as pd

def create_bar_chart(df, primary_var, secondary_var=None):
    if secondary_var:
        # Case 2: Stacked bar chart
        # Grouping by primary and secondary variable to get counts
        grouped_df = df.groupby([primary_var, secondary_var]).size().reset_index(name='count')
        fig = px.bar(grouped_df, x=primary_var, y='count', color=secondary_var, text='count')
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
        barmode='stack' if secondary_var else 'group',
        bargap=0.2  # Adjusts the gap between bars
    )

    fig.show()

# Example usage:
# Assuming df is your DataFrame and you have columns 'gender' and 'income'

# Example DataFrame
data = {
    'gender': ['Male', 'Female', 'Male', 'Female', 'Female', 'Male'],
    'income': ['Low', 'Medium', 'High', 'Medium', 'Low', 'High']
}

df = pd.DataFrame(data)

# Test the function with example DataFrame
create_bar_chart(df, 'gender')
create_bar_chart(df, 'gender', 'income')
