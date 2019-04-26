import dash
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go


# Initializes dash app
app = dash.Dash(__name__)

app.title = 'vdi visualisation'

VDI_DATA = {}


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


app.layout = html.Div(
    id='app-div',
    className='app',
    children=[
        dcc.Store(
            id='data-store',
            storage_type='session',
            data=VDI_DATA.copy()
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
                        figure=go.Figure(data=[]),
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
                            children='Run'
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
                                html_param_input('Zyklenwirkungsgrad', 76.6, '%'),
                                html_param_input('Entladetiefe', 37, '%'),
                                html_param_input('C-Rate', 0.5),
                            ]
                        ),
                        html.Div('Investitionskosten-div'),
                        html.Div('Betriebskosten-div'),
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
                            multi=False
                        )
                    ]
                ),
            ]

        )
    ],
)


if __name__ == '__main__':
    app.run_server(debug=True)
