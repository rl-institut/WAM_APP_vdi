import base64
import io
import numpy as np
import pandas as pd
import dash
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from vdi_oemof import oemof_results


# Initializes dash app
app = dash.Dash(__name__)

app.title = 'vdi visualisation'

VDI_DATA = {}
VDI_PARAM = {
    'params': {}
}


def html_param_input(p_name, p_value=0., p_unit='', **kwargs):
    """Create a nice html component for parameter inputs.

    :param p_name: (str) the label displayed to the left of the parameter input
    :param p_value: (number) the initial value of the parameter
    :param p_unit: (str) the unit displayed to the right of the parameter input
    :param kwargs: optional arguments for dcc.Input
    :return: a html.Div instance
    """

    p_label_name = p_name
    p_name = p_name.lower()

    return html.Div(
        id='{}-div'.format(p_name),
        className='app__input',
        children=[
            html.Div(
                id='{}-label'.format(p_name),
                className='app__parameter__label',
                children=p_label_name
            ),
            dcc.Input(
                id='{}-input'.format(p_name),
                className='app__parameter__input',
                type='number',
                value=p_value,
                **kwargs
            ),
            html.Div(
                id='{}-unit'.format(p_name),
                className='app__parameter__unit',
                children=p_unit
            ),
        ]
    )


def parse_upload_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.DataFrame()
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)

    return df.to_json()


app.layout = html.Div(
    id='app-div',
    className='app',
    children=[
        dcc.Store(
            id='data-store-results',
            storage_type='memory',
            data={}
        ),
        dcc.Store(
            id='data-store-param',
            storage_type='local',
            data=VDI_PARAM.copy()
        ),
        html.Div(
            id='top-panel-div',
            className='app__container',
            children=[
                html.Div(
                    id='timeseries-div',
                    className='app__timeseries',
                    title='Hover description',
                    children=dcc.Graph(
                        id='timeseries-plot',
                        figure=go.Figure(data=[go.Scatter(x=[], y=[])]),
                        style={'width': '70%', 'height': '90%'}
                    ),
                ),
                html.Div(
                    id='load-data-div',
                    className='app__load_data',
                    title='Hover description',
                    children=[
                        dcc.Upload(
                            id='load-data',
                            className='app__upload',
                            children=html.Div([
                                'Drag and Drop or ',
                                html.A('Select Files')
                            ]),
                            multiple=False,
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                        ),
                        html.Button(
                            id='run-btn',
                            className='app__button',
                            children='Run now'
                        )
                    ]
                )
            ]
        ),
        html.Div(
            id='bottom-panel-div',
            className='app__container',
            children=[
                html.Div(
                    id='parameters-div',
                    className='app__parameters',
                    title='Parameters description',
                    children=[
                        html.Div(
                            id='param-tech-div',
                            className='app__parameters__section',
                            children=[
                                html.Div('Technische Parameter'),
                                html_param_input('In_eff_akku', 76.6, '%'),
                                html_param_input('Entladetiefe', 37, '%'),
                                html_param_input('C-Rate', 0.5),
                            ]
                        ),
                        html.Div(
                            id='param-inv-div',
                            className='app__investparameters__section',
                            children=[
                                html.Div('Investitionskosten'),
                                html_param_input('Capex leist', 76.6, '%'),
                                ]
                        )
                    ]
                ),
                html.Div(
                    id='results-div',
                    className='app__results',
                    title='Results description',
                    children=[
                        html.Div('Ergebnisse'),
                        dcc.Dropdown(
                            id='country-input',
                            className='app__input__dropdown__map',
                            options=[],
                            value=None,
                            multi=False,
                        )
                    ]
                ),
            ]

        )
    ],
)

PARAM_LIST = [
    'capex_leist',
    'Entladetiefe'
]

PARAM_DICT = {
    'capex_leist': 'inflow_conversion_factor',
    'Entladetiefe': 'dkdkd'
}

param_id_list = [
    Input('{}-input'.format(p_name.lower()), 'value')
    for p_name in PARAM_LIST
]


@app.callback(
    Output('data-store-param', 'data'),
    [Input('load-data', 'contents')] + param_id_list,
    [
        State('load-data', 'filename'),
        State('data-store-param', 'data')
    ]
)
def update_data_param(
        contents,
        param1,
        param2,
        filenames,
        cur_data
):
    print(filenames, contents)

    if param1 is not None:
        cur_data['params'].update({PARAM_DICT['capex_leist']: param1})

    if param2 is not None:
        cur_data['params'].update({'was_function': param2})

    if contents is not None:
        cur_data.update({'csv_data':  parse_upload_contents(contents, filenames)})
    print(cur_data)
    return cur_data

@app.callback(
    Output('data-store-results', 'data'),
    [Input('run-btn', 'n_clicks')],
    [State('data-store-param', 'data')]
)
def compute_results(n_clicks, cur_params):
    print(cur_params)
    oemof_results(cur_params['params'])
    # ergebinis = oemof_results(param1=77.6, param2=37)
    # return ergebnis

if __name__ == '__main__':
    app.run_server(debug=True)

@app.callback(
    Output('timeseries-plot', 'figure'),
    [Input('data-store-param', 'data')],
    [State('timeseries-plot', 'figure')]
)
def update_graph(cur_data, fig):
    if cur_data is not None:
        data = cur_data.get('csv_data')
    else:
        data = None

    if data is not None:
        df = pd.read_json(cur_data['csv_data'])
        y = np.squeeze(df.values)
        x = [n * 0.25 for n in range(len(y))]
        fig['data'][0].update(
            {
                'x': x,
                'y': y,
            }
        )
    return fig

