# Import packages
from dash import Dash, html, dash_table, dcc, Output, Input, State, ctx  # callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from configurations.parser_configs import PARSER_CONFIG
import numpy as np
from datetime import date

# use callback function to generate config ??

currency_options = ['USD', 'EUR', 'GBP', 'JPY', 'HKD', 'CHF', 'CAD', 'NOK', 'DKK', 'SEK']
rates_benchmarks = ['SOFRRATE Index', 'ESTRON Index']


class DashApp:

    composition_table_default = pd.DataFrame({'Ticker': ['Dummy'], 'Region': ['EMEA'], 'Weight': [0.0]})
    store_name = 'app_store'
    graph_config = {}

    def __init__(self):
        # self.composition_table = pd.read_excel('./data/data1.xlsx', sheet_name=0)
        self.composition_table = self.composition_table_default
        self.clicked = False

        # Initialize the app
        external_stylesheets = [dbc.themes.CERULEAN]
        self.app = Dash(__name__, external_stylesheets=external_stylesheets)

        # generate drop down infos
        self.parser_configuration = [{'label': k, 'value': k} for k in PARSER_CONFIG.keys()]
        self.currency_options = [{'label': k, 'value': k} for k in currency_options]
        self.benchmark_options = [{'label': k.replace(' Index', ''), 'value': k} for k in rates_benchmarks]

        # generate callbacks
        self.app.callback(Output(component_id='controls-and-graph',
                                 allow_duplicate=False,
                                 component_property='figure'),
                          [Input(component_id='controls-and-radio-item', component_property='value'), ],
                          prevent_initial_call=True)(self.update_graph)

        self.app.callback(Output(component_id='controls-and-graph',
                                 allow_duplicate=True,
                                 component_property='figure'),
                          Input(component_id='my-radio-buttons-final', component_property='value'),
                          prevent_initial_call=True)(self.update_color)

        self.app.callback(Output(component_id='output-data-upload', component_property='data'),
                          Input('upload-data', 'contents'),
                          State('upload-data', 'filename'),
                          prevent_initial_call=True)(self.update_output)

        self.app.callback([Output(component_id='app_store',
                                  allow_duplicate=True,
                                  component_property='data'),
                           ],
                          [{'asset_name': Input('asset_name', 'value'),
                            'asset_currency': Input('asset_currency', 'value'),
                            'inception_level': Input('inception_level', 'value'),
                            'inception_date': Input('inception_date', 'date'),
                            'publication_calendar': Input('publication_calendar', 'value'),
                            'trading_calendar': Input('trading_calendar', 'value'),
                            'rebalancing_days': Input('rebalancing_days', 'value'),
                            'mark_iii': Input('mark_iii', 'value'),
                            'benchmark_rate': Input('benchmark_rate', 'value'),
                            'long_spread': Input('long_spread', 'value'),
                            'short_spread': Input('short_spread', 'value'),
                            # 'inception_level': Input('inception_level', 'value'),

                            'store': State(self.store_name, 'data')}],
                          prevent_initial_call=True)(self.update_store)

        self.app.callback(Output(component_id='app_store',
                                 allow_duplicate=True,
                                 component_property='data'),
                          [Input('random_button', 'n_clicks')],
                          prevent_initial_call=True)(self.random_value)

    def layout(self):
        # App layout
        self.app.layout = dbc.Container([

            dcc.Store(id=self.store_name, data={}),

            dbc.Row([
                html.Div('Onboarding Dashboard', className="text-primary text-center fs-3"),
                html.Hr(),
            ]),

            dbc.Row([

                # left column with basic information
                dbc.Col([

                    # first request index name
                    dbc.Row([
                        dbc.Col([
                            html.H6("Index Name"),
                        ]),
                        dbc.Col([
                            dcc.Input(id='asset_name', className="form-control", value='BOFAXYZ'),
                        ]),
                    ], ),
                    # html.Br(),

                    # index currency # TODO add option to manually override
                    dbc.Row([
                        dbc.Col([
                            html.H6("Index Currency"),
                        ]),
                        dbc.Col([
                            dcc.Dropdown(id='asset_currency',
                                         options=self.currency_options,
                                         value='USD'),
                        ]),
                    ], ),

                    # first request index name
                    dbc.Row([
                        dbc.Col([
                            html.H6("Start Level"),
                        ]),
                        dbc.Col([
                            dcc.Input(id='inception_level', className="form-control", value=100),
                        ]),
                    ], ),

                    # start date  # todo - limit to date T-1 and validate with publication calendar
                    dbc.Row([
                        dbc.Col([
                            html.H6("Start Date"),
                        ]),
                        dbc.Col([
                            dcc.DatePickerSingle(id='inception_date',
                                                 date=date.today(),
                                                 max_date_allowed=date.today(),
                                                 display_format='DD-MMM-YY'),
                        ]),
                    ], ),
                    html.Br(),

                    # publication calendar # TODO - add validation
                    dbc.Row([
                        dbc.Col([
                            html.H6("Publication Calendar"),
                        ]),
                        dbc.Col([
                            dcc.Input(id='publication_calendar', className="form-control", value='NOH',
                                      style=dict(display='flex', justifyContent='center')),
                        ]),
                    ], ),
                    # html.Br(),

                    # publication calendar # TODO - add validation
                    dbc.Row([
                        dbc.Col([
                            html.H6("Trading Calendar"),
                        ]),
                        dbc.Col([
                            dcc.Input(id='trading_calendar', className="form-control", value='NOH'),
                        ]),
                    ], ),
                    # html.Br(),

                    # publication calendar # TODO - add validation
                    dbc.Row([
                        dbc.Col([
                            html.H6("Rebalancing Days"),
                        ]),
                        dbc.Col([
                            dcc.Input(id='rebalancing_days', className="form-control", value='1'),
                        ]),
                    ], ),
                    html.Br(),

                    # Mark I or III ?
                    dbc.Row([
                        dbc.Col([
                            html.H6("Unit Based"),
                        ]),
                        dbc.Col([
                            dcc.Checklist(id='mark_iii', options=[{"label": "", "value": "MarkIII"}],
                                          className="form-check-input", value=[]),
                        ]),
                    ], ),

                    # benchmark rates # TODO can disable if not units based - allow overrides
                    dbc.Row([
                        dbc.Col([
                            html.H6("Benchmark Rate Based"),
                        ]),
                        dbc.Col([
                            dcc.Dropdown(id='benchmark_rate',
                                         options=self.benchmark_options,
                                         value='SOFRRATE Index'),
                        ]),
                    ], ),

                    # spread long leg # TODO can disable if not units based + validation
                    dbc.Row([
                        dbc.Col([
                            html.H6("Spread (Long Leg)"),
                        ]),
                        dbc.Col([
                            dcc.Input(id='long_spread', className="form-control", value=0),
                        ]),
                    ], ),

                    # spread short leg # TODO can disable if not units based + validation
                    dbc.Row([
                        dbc.Col([
                            html.H6("Spread (Short Leg)"),
                        ]),
                        dbc.Col([
                            dcc.Input(id='short_spread', className="form-control", value=0),
                        ]),
                    ], ),

                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),

                    dcc.Dropdown(options=[{'label': 'Sum', 'value': 'sum'},
                                          {'label': 'Count', 'value': 'count'},
                                          {'label': 'Average', 'value': 'avg'}],
                                 #  className="form-select",
                                 value='count',
                                 id='controls-and-radio-item'),

                    # html.Hr(),
                    # html.Div(children='Configuration'),
                    # dcc.Dropdown(options=self.parser_configuration,
                    #              value='parser_type', id='client_file_parser_reference'),

                    html.Hr(),
                    html.Div(children='Graph Color'),
                    dcc.RadioItems(options=[{'label': 'Blue  ', 'value': 'blue'},
                                            {'label': 'Green  ', 'value': 'green'},
                                            {'label': 'Red  ', 'value': 'red'}],
                                   value='blue',
                                   inline=True,
                                   #    className="form-check-input",
                                   #    className="btn-check",
                                   id='my-radio-buttons-final'),

                    ###########################################
                    html.Hr(),
                    html.Div(
                        [
                            html.H5("Selection Upload Browser"),
                            dcc.Upload(html.Button('Upload File', className='btn btn-primary'), id='upload-data', ),
                        ],
                        style={"max-width": "500px"},
                    ),

                    html.Hr(),
                    html.Div(
                        [
                            html.H5("Test Box"),
                            dcc.Input(id='box_text', className="form-control", value=0),
                            html.Button('Randomize This', className='btn btn-primary', id="random_button"),
                        ],
                        style={"max-width": "500px"},
                    ),
                ], width=3),

                ###########################################
                # right columns with tabs
                dbc.Col([
                    # dbc.Card(class_name="card text-white bg-primary mb-3", children= [

                    dcc.Tabs(id="tabs", value='all_tabs',
                             #  content_style={'tab_style': {"marginLeft": "auto"}},
                             className="nav nav-tabs",
                             children=[

                                 dcc.Tab(label='Custom Input', id='custom_input_tab', value='custom_input_tab',
                                         # style={'tab_style': {"marginLeft": "auto"}},
                                         className="nav-link",
                                         children=[
                                             html.Hr(),
                                             dash_table.DataTable(data=self.composition_table.to_dict('records'),
                                                                  page_size=25, style_table={'overflowX': 'auto'},
                                                                  style_header={'textAlign': 'left'},
                                                                  style_cell={'textAlign': 'left'},
                                                                  columns=[{'name': k, 'id': k} for k in
                                                                           self.composition_table.columns],
                                                                  editable=True,
                                                                  sort_action='native', filter_action='native',
                                                                  id="output-data-upload"),

                                         ]),

                                 dcc.Tab(label='Onboarding', id='onboarding_tab', value='onboarding_tab',
                                         className="nav-link",
                                         # tab_style={"marginLeft": "auto"},
                                         children=[
                                             html.Hr(),
                                             dbc.Row([
                                                 dcc.Graph(figure={}, id='controls-and-graph')
                                             ]),
                                         ]),

                                 dcc.Tab(label='JSON', id='json_tab', value='json_tab',
                                         className="nav-link",
                                         # tab_style={"marginLeft": "auto"},
                                         children=[
                                             html.Hr(),
                                         ]),

                                 dcc.Tab(label='Backtest', id='backtest', value='backtest',
                                         className="nav-link",
                                         # tab_style={"marginLeft": "auto"},
                                         children=[
                                             html.Hr(),
                                         ]),

                             ]),

                    # ]),

                ], width=9)
            ]),

            # ###########################################
            # html.Hr(),
            # dbc.Row([
            #     dcc.Graph(figure={}, id='controls-and-graph')
            # ]),

        ], fluid=True)

    def update_graph(self, func_chosen):
        self.graph_config['histfunc'] = func_chosen
        fig = px.histogram(self.composition_table, x='Region', y='Weight', **self.graph_config)
        return fig

    def update_color(self, color):
        self.graph_config['color_discrete_sequence'] = [color]
        fig = px.histogram(self.composition_table, x='Region', y='Weight', **self.graph_config)
        return fig

    def update_output(self, _, filename):
        print('getting data')
        self.composition_table = pd.read_excel('./data/%s' % filename, sheet_name=0) \
            if filename else self.composition_table_default
        print(self.composition_table[:4])
        return self.composition_table.to_dict('records')

    def update_store(self, **kwargs):
        """ update the strategy store """
        store = kwargs.get('store')
        store = store[0] if type(store) in (list, tuple) else store

        ref = ctx.triggered_id
        if ref != self.store_name:
            print(f'Replacing key {ref} = {store.get(ref)} with {kwargs.get(ref)}')
            store[ctx.triggered_id] = kwargs.get(ref)

        return [store]

    def random_value(self, _):
        new_val = str(int(np.round(np.random.random(1)[0] * 100, 0)))
        # self.value = new_val
        print(new_val)
        return [new_val]

    # starting point to run app
    def runApp(self, debug=True):
        self.layout()
        self.app.run(debug=debug)


# Run the app
if __name__ == '__main__':
    # from dash import __version__ as dv
    # print(dv)
    x = DashApp()
    x.runApp(debug=True)
