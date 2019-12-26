from db import *
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from modules.utils import *


def layout(encoded_flow):
    # print(f'encoded flow: {encoded_flow}')
    transitions = encoded_flow.split('=')
    # print(transitions)
    videos=[]
    for transition in transitions[0:-1]:
        transition = transition.split('&')
        transition = {'id':transition[0],'start time':transition[1]}
        # print(transition)
        videos.append(show_video(transition))
    return html.Div(videos,style={'width':'80%','margin':'0 auto'})
