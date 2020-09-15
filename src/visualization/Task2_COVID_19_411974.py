import pandas as pd
import numpy as np
import os,sys
import dash

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State

Data_Path=os.path.join(os.path.dirname(__file__),r'..\data')
Feature_Path=os.path.join(os.path.dirname(__file__),r'..\features')
Model_Path=os.path.join(os.path.dirname(__file__),r'..\models')


sys.path.insert(0, Data_Path)
sys.path.insert(0, Feature_Path)
sys.path.insert(0, Model_Path)
from SIR_methods import SIR_modelling

import plotly.graph_objects as go
from scipy import optimize
from scipy import integrate



dir_path_all=os.path.join(os.path.dirname(__file__),r'..\..\data\raw\COVID-19')
csv_DIR_path1=os.path.join(dir_path_all,r'..\..\processed' )
csv1_path1=os.path.join(csv_DIR_path1,'COVID_final_set.csv')
df_analyse = pd.read_csv(csv1_path1, sep = ';')

fig = go.Figure()
app = dash.Dash()
app.layout = html.Div([

    dcc.Markdown('''

    # Comparative study of Confirmed Cases and SIR Model
    
    
    Select the Country 
    

    '''),


    dcc.Dropdown(
        id = 'country_drop_down',
        options=[ {'label': each,'value':each} for each in df_analyse['country'].unique()],
        value= 'Germany', # Pre-Selected Country
        multi=False),

    dcc.Graph(figure = fig, id = 'SIR_graph')
    ])


@app.callback(
    Output('SIR_graph', 'figure'),
    [Input('country_drop_down', 'value')])

def SIR_figure_update(country_drop_down):

    traces = []

    dataframe_plot = df_analyse[df_analyse['country'] == country_drop_down]
    dataframe_plot = dataframe_plot[['state', 'country', 'confirmed','confirmed_filtered', 'date']].groupby(['country', 'date']).agg(np.sum).reset_index()
    dataframe_plot.sort_values('date', ascending = True).head()
    dataframe_plot = dataframe_plot.confirmed[40:]

    t, fitted = SIR_modelling(dataframe_plot)

    traces.append(dict (x = t,
                        y = fitted,
                        mode = 'markers',
                        opacity = .8,
                        name = 'SIR-Curve')
                  )

    traces.append(dict (x = t,
                        y = dataframe_plot,
                        mode = 'lines',
                        opacity = 0.8,
                        name = 'Original Data')
                  )

    return {
            'data': traces,
            'layout': dict (
                width=1300,
                height=800,
                title = 'SIR Model Fitting',

                xaxis= {'title':'Time-Span (Days)',
                       'tickangle':-45,
                        'nticks':20,
                        'tickfont':dict(size=16,color="#8f8f8f"),
                      },

                yaxis={'title': "Cases"}
        )
    }


if __name__ == '__main__':
    app.run_server(debug = True, use_reloader = False)
