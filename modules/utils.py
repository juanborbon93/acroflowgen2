from db import *
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc

@db_session()
def show_video(transition,show_title=True):
    start = Transitions[transition].start.name
    end = Transitions[transition].end.name
    youtube_id = transition
    video = html.Div([
        html.Iframe(
                src= f"https://www.youtube.com/embed/{youtube_id}?autoplay=1&loop=1",
                style={
                    'position': 'absolute',
                    'top': '0',
                    'left': '0',
                    'width': '100%',
                    'height': '100%'
                }
            )
        ],
        style={
            'position': 'relative',
            'padding-bottom': '56.25%',
            'height': '0',
            'width':'100%'
        }
    )
    if show_title:
        return html.Div(
            [
                html.H2(f'{start} to {end}'),
                video
            ]
        )
    else: 
        return html.Div([video])
