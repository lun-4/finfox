#!/usr/bin/env python3
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from decimal import Decimal
from plotly.subplots import make_subplots

import csv

df = pd.read_csv(sys.argv[1])
grouped_df = df.groupby("month")
data = [x for x in grouped_df]
data.sort(key=lambda x: int(x[0].split("-")[1]))


def title(entry):
    month, data = entry
    full_amount = Decimal(0)
    for row in data.values:
        _month, _category, amount_string = row
        full_amount += Decimal(amount_string)
    full_amount = round(full_amount, 2)
    return f"{month} ({full_amount})"


# Create a subplot with one row and one column
fig = make_subplots(
    rows=4,
    cols=4,
    subplot_titles=[title(entry) for entry in data],
    print_grid=True,
    specs=[
        [
            {"type": "pie"},
        ]
        * 4,
    ]
    * 4,
)

# Iterate through each group (month) and create a pie chart
row, col = 1, 1

for i, (month, group_data) in enumerate(data, 1):
    print(i, month, group_data)
    category_labels = group_data["category"]
    amount_values = group_data["amount"]

    pie_chart = go.Pie(labels=category_labels, values=amount_values)
    fig.add_trace(pie_chart, row=row, col=col)

    # lol, actually doing maths? nah bruh an if solves the problem
    if i % 4 == 0:
        col = 1
        row += 1
    else:
        col += 1


# Update the layout and display the combined pie chart
fig.update_layout(
    showlegend=False, title_text=f"financial reports for each month ({sys.argv[1]})"
)
fig.show()
