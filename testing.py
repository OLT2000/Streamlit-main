import plotly
import json

with open("distribution_of_countries_by_panel.json", "r") as f:
    # plot_json = json.load(f)

    fig = plotly.io.read_json(f, engine="json")
fig.show() 