import dash
import dash_bootstrap_components as dbc
from flask import Flask
server = Flask(__name__)#app.server
external_js = [
    {
        'src':"https://www.googletagmanager.com/gtag/js?id=UA-155021355-1",
        'async':True
    }
]
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],external_scripts=external_js,server=server)
# app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions']=True