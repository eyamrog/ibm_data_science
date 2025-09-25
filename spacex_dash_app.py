# Hi! I launched a skeleton app named `spacex_dash_app.py`. Pressing `CTRL+C` would not make it quit...
# It’s a common Dash/Flask behaviour on Windows/Some terminals. Try this on Windows PowerShell:
#   netstat -ano | findstr :8050
#   taskkill /PID <pid> /F

# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] + [
                                        {'label': site, 'value': site}
                                        for site in sorted(spacex_df['Launch Site'].unique())
                                    ],
                                    value='ALL',
                                    placeholder='Select a Launch Site here',
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_success_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(
            spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='successes'),
            values='successes',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = df_site['class'].value_counts().rename_axis('Outcome').reset_index(name='Count')
        counts['Outcome'] = counts['Outcome'].map({1: 'Success', 0: 'Failed'})
        fig = px.pie(
            counts,
            values='Count',
            names='Outcome',
            title=f'Success vs. Failed Launches for site {selected_site}'
        )
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_success_payload_scatter(selected_site, payload_range):
    low, high = payload_range
    df_filtered = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
        ]
    if selected_site != 'ALL':
        df_filtered = df_filtered[df_filtered['Launch Site'] == selected_site]

    title = 'Correlation between Payload and Success for all Sites' if selected_site == 'ALL' \
        else f'Correlation between Payload and Success for {selected_site}'

    fig = px.scatter(
        df_filtered,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title
    )
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
