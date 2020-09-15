import pandas as pd
import numpy as np
import subprocess
import dash
import sys
dash.__version__
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State

import plotly.graph_objects as go

from sklearn import linear_model
reg = linear_model.LinearRegression(fit_intercept=True)


from scipy import signal
import os

Data_Path=os.path.join(os.path.dirname(__file__),r'..\data')
Feature_Path=os.path.join(os.path.dirname(__file__),r'..\features')
Model_Path=os.path.join(os.path.dirname(__file__),r'..\models')

import sys
sys.path.insert(0, Data_Path)
sys.path.insert(0, Feature_Path)
sys.path.insert(0, Model_Path)


from get_dataset import get_data_jh
from processed_JH_dataset import store_rel_JHdataset
from get_processed_all import processed_result_all
from build_features import *


get_data_jh()
store_rel_JHdataset()
processed_result_all()

print(os.getcwd())
dir_path_all=os.path.join(os.path.dirname(__file__),r'..\..\data\raw\COVID-19')
csv_DIR_path1=os.path.join(dir_path_all,r'..\..\processed' )
csv1_path1=os.path.join(csv_DIR_path1,'COVID_final_set.csv')
df_ip_all=pd.read_csv(csv1_path1,sep=';')


fig = go.Figure()

app = dash.Dash()
app.layout = html.Div([

    dcc.Markdown('''
    ##           **COVID-19 ANALYSIS PROTOTYPING DASHBOARD (A Project on Enterprise Datascience)**
    
    + This part of the Task (Task-1) gives the timelines of different countries based on the feature selected by the user.

    '''),

    dcc.Markdown('''
    ## Country For Visualization (Multi-select)
    '''),


    dcc.Dropdown(
        id='country_drop_down',
        options=[ {'label': each,'value':each} for each in df_ip_all['country'].unique()],
        value=['Germany','India','Italy','US',], # These are the pre-selected countries which will be showed on the dashboard by-default.
        multi=True
    ),

    dcc.Markdown('''
        ## Select desired Timeline feature.
        '''),


    dcc.Dropdown(
    id='doubling_time',
    options=[
        {'label': 'Timeline - Confirmed ', 'value': 'confirmed'},
        {'label': 'Timeline - Confirmed (Filtered)', 'value': 'confirmed_filtered'},
        {'label': 'Timeline - Doubling Rate', 'value': 'confirmed_DR'},
        {'label': 'Timeline - Doubling Rate (Filtered)', 'value': 'confirmed_filtered_DR'},
    ],
    value='confirmed',
    multi=False
    ),

    dcc.Graph(figure=fig, id='main_window_slope')
])



@app.callback(
    Output('main_window_slope', 'figure'),
    [Input('country_drop_down', 'value'),
    Input('doubling_time', 'value')])


def fig_update(list_of_countries,s_doubling):


    if 'confirmed' == s_doubling:
        my_yaxis={'type':"log",
                  'title':'Confirmed Cases (Source: Johns Hopkins CSSE (log-scale))'
              }
    elif 'confirmed_filtered' == s_doubling:
        my_yaxis={'type':"log",
                  'title':'Confirmed Cases- Filtered (Source: Johns Hopkins CSSE (log-scale))'
              }
    elif 'confirmed_DR' == s_doubling:
        my_yaxis={'type':"log",
               'title':'Approx. Doubling Rate (Source: Johns Hopkins CSSE (log-scale))'
              }
    elif 'confirmed_filtered_DR' == s_doubling:
        my_yaxis={'type':"log",
               'title':'Approx. Doubling Rate- Filtered (Source: Johns Hopkins CSSE (log-scale))'
              }
        

    traces = []
    for each in list_of_countries:

        df_plot=df_ip_all[df_ip_all['country']==each]

        if s_doubling=='doubling_rate_filtered':
            df_plot=df_plot[['state','country','confirmed','confirmed_filtered','confirmed_DR','confirmed_filtered_DR','date']].groupby(['country','date']).agg(np.mean).reset_index()
        else:
            df_plot=df_plot[['state','country','confirmed','confirmed_filtered','confirmed_DR','confirmed_filtered_DR','date']].groupby(['country','date']).agg(np.sum).reset_index()
  


        traces.append(dict(x=df_plot.date,
                                y=df_plot[s_doubling],
                                mode='markers+lines',
                                opacity=0.8,
                                name=each
                        )
                )

    return {
            'data': traces,
            'layout': dict (
                width=1250,
                height=800,

                xaxis={'title':'Timeline',
                        'tickangle':-45,
                        'nticks':20,
                        'tickfont':dict(size=15,color="#7f7f7f"),
                      },

                yaxis=my_yaxis
        )
    }





if __name__ == '__main__':

    app.run_server(debug=True, use_reloader=False)
