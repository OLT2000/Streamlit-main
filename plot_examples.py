import plotly.express as px
import pandas as pd

"""
1. Stacked Bar Chart
A stacked bar chart displays bars divided into segments, representing sub-groups of the category. It shows the total size of groups and the proportional sizes of sub-groups.

Aggregations
Count: Total count of items in each category.
Sum: Total sum of values in each category.
Mean/Median: Average value in each category.
Custom: Any custom aggregation that fits the data structure.

Variables
Primary Variable: Categories displayed on the x-axis.
Secondary Variable: Sub-groups represented as segments within the bars.
"""
df = pd.DataFrame({
    'Category': ['A', 'A', 'B', 'B'],
    'Sub-Category': ['X', 'Y', 'X', 'Y'],
    'Value': [10, 20, 30, 40]
})
fig = px.bar(df, x='Category', y='Value', color='Sub-Category', barmode='stack')
fig.update_layout(title_text="Stacked Bar")
fig.show()

"""
2. Mekko Chart
A Mekko chart, also known as a Marimekko chart, is used to visualize categorical data across two dimensions, with varying widths and heights of the segments.

Aggregations
Count: Number of items per category.
Sum: Sum of values in each category.

Variables
Two Variables: Displayed along the x and y axes with segments within each category.
"""
import plotly.graph_objects as go
import numpy as np

labels = ["apples","oranges","pears","bananas"]
widths = np.array([10,20,20,50])

data = {
    "South": [50,80,60,70],
    "North": [50,20,40,30]
}

fig = go.Figure()
for key in data:
    fig.add_trace(go.Bar(
        name=key,
        y=data[key],
        x=np.cumsum(widths)-widths,
        width=widths,
        offset=0,
        customdata=np.transpose([labels, widths*data[key]]),
        texttemplate="%{y} x %{width} =<br>%{customdata[1]}",
        textposition="inside",
        textangle=0,
        textfont_color="white",
        hovertemplate="<br>".join([
            "label: %{customdata[0]}",
            "width: %{width}",
            "height: %{y}",
            "area: %{customdata[1]}",
        ])
    ))

fig.update_xaxes(
    tickvals=np.cumsum(widths)-widths/2,
    ticktext= ["%s<br>%d" % (l, w) for l, w in zip(labels, widths)]
)

fig.update_xaxes(range=[0,100])
fig.update_yaxes(range=[0,100])

fig.update_layout(
    title_text="Marimekko Chart",
    barmode="stack",
    uniformtext=dict(mode="hide", minsize=10),
)
# fig.write_image("mekko.png")

"""
3. Spider Chart
A spider chart, or radar chart, is used to compare multiple variables on a two-dimensional plane with a separate axis for each variable.

Aggregations
Mean/Median: Average value of variables.
Sum: Total value of variables.

Variables
Multiple Variables: Displayed as axes emanating from the center.
"""
df = pd.DataFrame({
    'Variable': ['V1', 'V2', 'V3'],
    'A': [10, 40, 70],
    'B': [20, 50, 80],
    'C': [30, 60, 90]
})
fig = px.line_polar(df, r=['A', 'B', 'C'], theta='Variable', line_close=True)
fig.update_layout(title_text="Spider")

fig.show()

"""
4. Area Chart
An area chart is used to show trends over time or categories. It is similar to a line chart but with the area under the line filled.

Aggregations
Sum: Total value over time.
Mean/Median: Average value over time.
Count: Number of occurrences over time.

Variables
One Primary Variable: Time or categories on the x-axis.
One or More Secondary Variables: Values represented as areas.
"""

import plotly.express as px
df = pd.DataFrame({
    'Time': ['T1', 'T2', 'T3'],
    'A': [10, 40, 70],
    'B': [20, 50, 80],
    'C': [30, 60, 90]
})
fig = px.area(df, x='Time', y=['A', 'B', 'C'])
fig.update_layout(title_text="Area")

fig.show()

"""
5. Waterfall Chart
A waterfall chart shows the cumulative effect of sequentially introduced positive or negative values, often used in financial analysis.

Aggregations
Sum: Incremental changes in values.

Variables
Primary Variable: Categories along the x-axis.
Secondary Variable: Values contributing to changes.
"""
import plotly.graph_objects as go
fig = go.Figure(go.Waterfall(
    x = ["Start", "Increase", "Decrease", "End"],
    measure = ["absolute", "relative", "relative", "total"],
    y = [100, 30, -20, 110]
))
fig.update_layout(title_text="Waterfall")

fig.show()

"""
6. Bubble Chart
A bubble chart is a scatter plot where a third dimension is represented by the size of the bubbles.

Aggregations
Count: Frequency of occurrences.
Sum/Mean: Value represented by bubble size.

Variables
Three Variables: X-axis, Y-axis, and bubble size.
"""
import plotly.express as px
df = pd.DataFrame({
    'X': [1, 2, 3],
    'Y': [2, 3, 4],
    'Size': [10, 20, 30]
})
fig = px.scatter(df, x='X', y='Y', size='Size')
fig.update_layout(title_text="Bubble")

fig.show()


"""
7. Bar with Line Chart
A bar with line chart combines a bar chart and a line chart to show two different types of information on the same plot.

Aggregations
Sum/Count/Mean: For bars.
Sum/Count/Mean: For line.

Variables
Two Variables: One for bars, one for line.
"""
import plotly.graph_objects as go
df = pd.DataFrame({
    'Category': ['A', 'B', 'C'],
    'Bar Value': [10, 20, 30],
    'Line Value': [15, 25, 35]
})
fig = go.Figure()
fig.add_trace(go.Bar(x=df['Category'], y=df['Bar Value'], name='Bar'))
fig.add_trace(go.Scatter(x=df['Category'], y=df['Line Value'], name='Line', yaxis='y2'))

fig.update_layout(
    title_text="Bar w line",
    yaxis2=dict(
        overlaying='y',
        side='right'
    )
)
fig.show()

"""
8. Football Field Chart
A football field chart is used to show ranges of values, often used in financial modeling to represent scenarios.

Aggregations
Ranges: Minimum, maximum, and various percentiles.

Variables
Single Variable: Representing different ranges.
Table Structure
"""
import plotly.graph_objects as go
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[10, 50],
    y=[1, 1],
    mode='lines',
    line=dict(color='grey', width=2),
    name='Range'
))

fig.add_trace(go.Scatter(
    x=[20, 40],
    y=[1, 1],
    mode='lines',
    line=dict(color='blue', width=10),
    name='Interquartile Range'
))

fig.update_layout(
    title_text="football",
    xaxis_title='Value',
    yaxis_title='Scenario',
    showlegend=True
)

fig.show()

"""
9. Cluster Bar Chart
A cluster bar chart displays bars grouped by categories, allowing comparison of multiple variables across categories.

Aggregations
Count/Sum/Mean: Values represented by bars.

Variables
Multiple Variables: Grouped within each category.
"""
import plotly.express as px
df = pd.DataFrame({
    'Category': ['A', 'A', 'B', 'B'],
    'Group': ['X', 'Y', 'X', 'Y'],
    'Value': [10, 20, 30, 40]
})
fig = px.bar(df, x='Category', y='Value', color='Group', barmode='group')
fig.update_layout(title_text="Cluster Bar")

fig.show()

"""
Marimekko #2
"""
import plotly.express as px
import pandas as pd

# Sample data
data = {
    'Category': ['A', 'A', 'B', 'B', 'C', 'C'],
    'Subcategory': ['X', 'Y', 'X', 'Y', 'X', 'Y'],
    'Value': [5, 10, 10, 20, 20, 30]
}

df = pd.DataFrame(data)

# Calculate total values for categories and subcategories
total_category = df.groupby('Category')['Value'].sum().reset_index()
total_subcategory = df.groupby(['Category', 'Subcategory'])['Value'].sum().reset_index()

# Merge totals with original dataframe
df = df.merge(total_category, on='Category', suffixes=('', '_total'))
df = df.merge(total_subcategory, on=['Category', 'Subcategory'], suffixes=('', '_sub_total'))

# Calculate widths and heights
df['Width'] = df['Value_total'] / df['Value_total'].sum()
df['Height'] = df['Value'] / df['Value_total']

# Plotting Marimekko chart using Plotly Express
fig = px.bar(df, 
             x='Category', 
             y='Height', 
             color='Subcategory', 
             text='Value', 
             title='Marimekko Chart',
             width=800, 
             height=600)

# # Modify bar widths
# for i, cat in enumerate(df['Category'].unique()):
#     fig.data[i].width = df[df['Category'] == cat]['Width'].values[0]

# Update layout for better visualization
fig.update_layout(barmode='stack', 
                  xaxis={'categoryorder':'total descending'}, 
                  xaxis_title='Category', 
                  yaxis_title='Proportion')

fig.show()
