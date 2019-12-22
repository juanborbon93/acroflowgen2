import dash
import dash_bootstrap_components as dbc
from flask import Flask
server = Flask(__name__)#app.server
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],server=server)
app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions']=True