import datetime
import textwrap

import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from flask import request

from app import app, batch_get_data
from config import API_HOST
from design import CONFIG_OPTIONS, DISCRETE_COLORS, LABELS, apply_figure_style, DISCRETE_COLORS_MAP


pretty_columns = {
    'srnumber': "SR Number",
    'createdDate': "Created Date",
    'closedDate': "Closed Date",
    'typeName': "Type Name",
    'agencyName': "Agency Name",
    'sourceName': "Source Name",
    'address': "Address"
}

START_DATE_DELTA = 7
END_DATE_DELTA = 1
start_date = datetime.date.today() - datetime.timedelta(days=START_DATE_DELTA)
end_date = datetime.date.today() - datetime.timedelta(days=END_DATE_DELTA)

# TITLE
title = "NEIGHBORHOOD WEEKLY REPORT"

# DATA
df_path = f"/requests/updated?start_date={start_date}&end_date={end_date}"
print(" * Downloading data for dataframe")
df = batch_get_data(API_HOST + df_path)
df['createdDate'] = pd.to_datetime(
    df['createdDate'], errors='coerce').dt.strftime('%Y-%m-%d')
df['closedDate'] = pd.to_datetime(
    df['closedDate'], errors='coerce').dt.strftime('%Y-%m-%d')
print(" * Dataframe has been loaded")

try:
    selected_council = request.args.get('councilName') or 'Arleta'
except (RuntimeError):
    selected_council = 'Arleta'

table_df = df.query(f"councilName == '{selected_council}'")[['srnumber', 'createdDate', 'closedDate', 'typeName', 'agencyName', 'sourceName', 'address']]  # noqa

req_type_line_base_graph = px.line()
apply_figure_style(req_type_line_base_graph)

req_type_pie_base_graph = px.pie()
apply_figure_style(req_type_pie_base_graph)

# Populate the neighborhood dropdown


def populate_options():
    council_df_path = '/councils'
    council_df = pd.read_json(API_HOST + council_df_path)
    values = []
    for i in council_df.sort_values('councilName').councilName.unique():
        values.append({
            'label': i,
            'value': i
        })
    return values


# Layout
layout = html.Div([
    html.H1(title),
    dcc.Dropdown(
        id='council_list',
        clearable=False,
        value=selected_council,
        placeholder="Select a neighborhood",
        options=populate_options()
    ),
    html.Div(f"Weekly report ({start_date.strftime('%b %d')} to {end_date.strftime('%b %d')})"),  # noqa
    html.Div([
        html.Div(
            [html.H2(id="created_txt"), html.Label("New Requests")],
            className="stats-label"
        ),
        html.Div(
            [html.H2(id="closed_txt"), html.Label("Closed Requests")],
            className="stats-label"
        ),
        html.Div(
            [html.H2(id="net_txt"), html.Label("Net Change")],
            className="stats-label"
        ),
    ], className="graph-row"),
    html.Div([
        html.Div(
            dcc.Graph(id='graph', figure=req_type_line_base_graph, config=CONFIG_OPTIONS),
            className="half-graph"
        ),
        html.Div(
            dcc.Graph(id='pie_graph', figure=req_type_pie_base_graph, config=CONFIG_OPTIONS),
            className="half-graph"
        )
    ]),
    html.Div(
        dash_table.DataTable(
            id='council_table',
            columns=[
                {"name": pretty_columns[i], "id": i} for i in table_df.columns
            ],
            style_as_list_view=True,
            style_cell={
                'padding': '5px',
                'textAlign': 'left',
                'fontFamily': 'Roboto, Arial',
                'fontSize': 12,
                'color': '#333333',
                'backgroundColor': '#EEEEEE',
            },
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold'
            },
            sort_action='native',
            # filter_action='native',
            page_size=20,
        )
    )
])


# Define callback to update graph
@app.callback(
    Output("council_table", "data"),
    Input("council_list", "value")
)
def update_table(selected_council):
    table_df = df.query(f"councilName == '{selected_council}'")[['srnumber', 'createdDate', 'closedDate', 'typeName', 'agencyName', 'sourceName', 'address']]  # noqa
    # The following check is to ensure Dash graphs are populated with dummy data when query returns empty dataframe.
    if table_df.shape[0] == 0:
        table_df = pd.DataFrame(columns=["Request Type"])
        for i, request_type in enumerate(DISCRETE_COLORS_MAP):
            table_df.loc[i] = [request_type]
    return table_df.to_dict('records')


@app.callback(
    [
        Output("created_txt", "children"),
        Output("closed_txt", "children"),
        Output("net_txt", "children"),
    ],
    Input("council_list", "value")
)
def update_text(selected_council):
    create_count = df.query(f"councilName == '{selected_council}' and createdDate >= '{start_date}'")['srnumber'].count()  # noqa
    close_count = df.query(f"councilName == '{selected_council}' and closedDate >= '{start_date}'")['srnumber'].count()  # noqa
    # This check is to ensure data quality issues don't flow downstream to the dashboard (i.e., closed requests exist without any new requests).
    if create_count == 0 and close_count > 0:
        return 0, 0, 0
    else:
        return create_count, close_count, create_count - close_count


@app.callback(
    Output("graph", "figure"),
    Input("council_list", "value")
)
def update_figure(selected_council):
    figure_df = df.query(f"councilName == '{selected_council}' and createdDate >= '{start_date}'").groupby(['createdDate', 'typeName'])['srnumber'].count().reset_index()  # noqa
    # The following check is to ensure Dash graphs are populated with dummy data when query returns empty dataframe.
    if figure_df.shape[0] == 0:
        figure_df = pd.DataFrame(columns=["createdDate", "srnumber", "typeName"])
        for j in range(START_DATE_DELTA):
            for request_type in DISCRETE_COLORS_MAP:
                figure_df.loc[j] = [start_date + datetime.timedelta(days=j), 0, request_type]
    figure_df.typeName = figure_df.typeName.map(lambda x: '<br>'.join(textwrap.wrap(x, width=16)))  # noqa
    fig = px.line(
        figure_df,
        x="createdDate",
        y="srnumber",
        color="typeName",
        color_discrete_sequence=DISCRETE_COLORS,
        labels=LABELS,
        title="New Requests"
    )
    fig.update_xaxes(
        tickformat="%a\n%m/%d",
    )
    fig.update_traces(
        mode='markers+lines'
    )  # add markers to lines

    apply_figure_style(fig)

    return fig


@app.callback(
    Output("pie_graph", "figure"),
    Input("council_list", "value")
)
def update_council_figure(selected_council):
    pie_df = df.query(f"councilName == '{selected_council}' and createdDate >= '{start_date}'").groupby(['typeName']).agg('count').reset_index()  # noqa
    if pie_df.shape[0] == 0:
        pie_df = pd.DataFrame(columns=["srnumber", "typeName"])
        for i, request_type in enumerate(DISCRETE_COLORS_MAP):
            pie_df.loc[i] = [0, request_type]
    pie_fig = px.pie(
        pie_df,
        names="typeName",
        values="srnumber",
        color_discrete_sequence=DISCRETE_COLORS,
        labels=LABELS,
    )

    apply_figure_style(pie_fig)

    return pie_fig
