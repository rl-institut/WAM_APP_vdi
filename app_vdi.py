import base64
import io
import json
import numpy as np
import pandas as pd
import dash
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pprint as pp
from bookkeeping import simulate_energysystem


# Initializes dash app
app = dash.Dash(__name__)

# Load css file
external_css = [
    'https://raw.githack.com/rl-institut/WAM/dev/static/foundation/css/app.css',
]
for css in external_css:
    app.css.append_css({"external_url": css})

app.title = 'vdi visualisation'

VDI_RESULTS = {
    'results': {}
}

VDI_PARAM = {
    'params': {}
}


def html_param_output(p_name, p_value=0., p_unit='', **kwargs):
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
                className='app__parameter__output',
                type='text',
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

def parse_upload_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    return df.to_json()


app.layout = html.Div(
    className='grid-y medium-grid-frame',
    children=[
        dcc.Store(
            id='data-store-results',
            storage_type='local',
            data=VDI_RESULTS.copy()
        ),
        dcc.Store(
            id='data-store-param',
            storage_type='session',
            data=VDI_PARAM.copy()
        ),
        html.Div(
            id='header-div',
            className='cell large- shrink header',
            children=[
                html.Div(
                    id='header-content',
                    className='grid-x grid-margin-x',
                    children=[
                        html.Div(
                            className='cell small-4 text-justify',
                            children='Title'
                        ),
                        html.Div(
                            className='cell small-8 text-justify',
                            children='Subtitle',
                        ),
                    ]
                ),
            ]
        ),
        html.Div(
            id='page-div',
            className='cell medium-10',
            children=[
                html.Div(
                    id='app-div',
                    className='grid-y',
                    children=[
                        html.Div(
                            className='cell large-7',
                            children=[
                                html.Div(
                                    className='grid-x',
                                    children=[
                                        html.Div(
                                            id='timeseries-div',
                                            className='cell large-9',
                                            title='electrical demand',
                                            children=dcc.Graph(
                                                id='timeseries-plot',
                                                figure=go.Figure(
                                                    data=[
                                                        go.Scatter(
                                                            x=[],
                                                            y=[],
                                                            mode='markers'
                                                        )
                                                    ]
                                                ),
                                            ),
                                        ),
                                        html.Div(
                                            id='load-data-div',
                                            className='cell large-3',
                                            title='Here should be load the data series file (electric demand)',
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
                                )
                            ]
                        ),
                        html.Div(
                            className='cell large-5',
                            children=[
                                html.Div(
                                    id='input div',
                                    className='grid-x',
                                    children=[
                                        html.Div(
                                            id='param-tech-div',
                                            className='cell auto',
                                            children=[
                                                html.Div('Technische Parameter'),
                                                html_param_input('Zyklenwirkungsgrad', 76.6, '%'),
                                                html_param_input('Entladetiefe', 37, '%'),
                                                html_param_input('C-Rate', 0.5),
                                            ]
                                        ),
                                        html.Div(
                                            id='param-opex-div',
                                            className='cell auto',
                                            children=[
                                                html.Div('Investitionskosten'),
                                                html_param_input('leistungbezogene', 175, 'euro/kW'),
                                                html_param_input('Kapazitaetbezogene', 237, 'euro/kWh'),
                                                html_param_input('Zeitraum', 10, 'Jahr'),
                                                html_param_input('Kalkulationszinsatz', 7, '%'),
                                            ]
                                        ),
                                        html.Div(
                                            id='param-capex-div',
                                            className='cell auto',
                                            children=[
                                                html.Div('Betriebskosten'),
                                                html_param_input('Leistungspreis', 87, 'Euro/kW ° a'),
                                                html_param_input('Stromkosten', 0.1537, 'Euro/kWh'),
                                                html_param_input('Speichernkosten', 10, 'Euro/kW ° a'),
                                            ]
                                        ),
                                    ]
                                ),
                                html.Div(
                                    id='output-div',
                                    className='grid-x',
                                    children=[
                                        html.Div(
                                            className='cell auto',
                                            title='Results Model',
                                            children=[
                                                html.Div('Ergebnisse'),
                                                html_param_output('Kostenreduktion', 0, 'Euro'),
                                                html_param_output('Amortizationsdauer', 0, 'Jahre'),
                                                html_param_output('Speicherleistung', 0, 'kW'),
                                                html_param_output('Speicherkapazität', 0, 'kWh'),
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                # html.Div(
                #     id='footer-div',
                #     className='cell shrink footer',
                #     children=[
                #         html.Div(
                #             id='footer-content',
                #             className='grid-x grid-margin-x',
                #             children=['LOGOs LOGO IMPRESSUM']
                #
                #         )
                #     ]
                # ),
            ]
        )
    ]
)

# List of parameters to be read from the App interface and handled to the Oemof-Model
# this need to correspond to the ones configured in the Layout (up), and from this point
# the order in which they are given needs to remain unchanged.
PARAM_LIST = [
    'Entladetiefe',
    'Leistungspreis',
    'Stromkosten',
    'Speichernkosten',
    'Kalkulationszinsatz',
    'leistungbezogene',
    'Kapazitaetbezogene',
    'Zeitraum',
    'Zyklenwirkungsgrad',
    'C-Rate',
]

# Name translation between App and Oemof-Model
PARAM_DICT = {
    'Entladetiefe': 'capmin',
    'Leistungspreis': 'powercost',
    'Stromkosten': 'electcost',
    'Speichernkosten': 'batt_betrieb',
    'Kalkulationszinsatz': 'interest_r',
    'leistungbezogene': 'batt_pow_cost',
    'Kapazitaetbezogene': 'batt_cap_cost',
    'Zeitraum': 'inv_period',
    'Zyklenwirkungsgrad': 'effic',
    'C-Rate': 'c_rate',
}

# Assignation of the values collected in the App interface to their corresponding names
param_id_list = [
    Input('{}-input'.format(p_name.lower()), 'value')
    for p_name in PARAM_LIST
]

@app.callback( #updating dcc param when a inputs are modified or timeseries is loaded
    Output('data-store-param', 'data'),
    [  # The uploading of the time series and the modification of a parameter
        # are defined as triggers (and arguments).
        Input('load-data', 'contents')
    ] + param_id_list,
    [   # The filename collected with for the time series and the previous data
        # already stored in the parameter dcc are also included as arguments.
        State('load-data', 'filename'),
        State('data-store-param', 'data')
    ]
)
def update_data_param(
        # Here the order of inputs muss again be the same as above. Notice that it
        # follows the "input" and "state" declarations: contents,
        # param_id_list[Entladetiefe,...], filename, data (cur_param).
        contents,
        Entladetiefe,
        Leistungspreis,
        Stromkosten,
        Speichernkosten,
        Kalkulationszinsatz,
        leistungbezogene,
        Kapazitaetbezogene,
        Zeitraum,
        Zyklenwirkungsgrad,
        CRate,
        filenames,
        cur_param
):
    param_value_list = [
        Entladetiefe,
        Leistungspreis,
        Stromkosten,
        Speichernkosten,
        Kalkulationszinsatz,
        leistungbezogene,
        Kapazitaetbezogene,
        Zeitraum,
        Zyklenwirkungsgrad,
        CRate,
    ]
    # If the previous order was followed, each collected value on the interface
    # will be correctly assigned to a key here, packed in a Dictionary and ultimately
    # handed on to the Oemof-Model

    for p, n in zip(param_value_list, PARAM_LIST):
        if p is not None:
            cur_param['params'].update({PARAM_DICT[n]: p})

    if contents is not None:
        cur_param.update({'csv_data': parse_upload_contents(contents)})
        cur_param.update({'csv_name': filenames})
    return cur_param

@app.callback( #updating results dcc when button click
    Output('data-store-results', 'data'),
    [Input('run-btn', 'n_clicks')],
    [
        State('data-store-param', 'data'),
        State('data-store-results', 'data')
    ]
)
def compute_results(n_clicks, cur_param_data, cur_res_data):
    if n_clicks is not None:
        results_model = simulate_energysystem(cur_param_data)

        cur_res_data.update(results_model)
    return cur_res_data

@app.callback( #updating Result inputs when results dcc changes (kostenreduktion)
    Output('kostenreduktion-input', 'value'),
    [
        Input('data-store-results', 'data')
    ]
)
def compute_kostenreduktion(cur_output):
    answer = None
    if cur_output is not None:

        answer = cur_output.get('kostenreduktion')

    return answer


@app.callback( #updating Result inputs when results dcc changes (amortizationsdauer)
    Output('amortizationsdauer-input', 'value'),
    [
        Input('data-store-results', 'data')
    ]
)
def compute_amortizationsdauer(cur_output):
    answer = None
    if cur_output is not None:

        answer = cur_output.get('amortizationsdauer')

    return answer

@app.callback( #updating Result inputs when results dcc changes (speicherleistung)
    Output('speicherleistung-input', 'value'),
    [
        Input('data-store-results', 'data')
    ]
)
def compute_speicherleistung(cur_output):
    answer = None
    if cur_output is not None:

        answer = cur_output.get('speicherleistung')

    return answer

@app.callback( #updating Result inputs when results dcc changes (speicherkapazität)
    Output('speicherkapazität-input', 'value'),
    [
        Input('data-store-results', 'data')
    ]
)
def compute_speicherkapazität(cur_output):
    answer = None
    if cur_output is not None:

        answer = cur_output.get('speicherkapazität')

    return answer

@app.callback(  # Updating plot when dcc parameters change
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
        fig['data'][0].update(
            {
                'x': df.timestep,
                'y': df.demand_el,
            }
        )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

