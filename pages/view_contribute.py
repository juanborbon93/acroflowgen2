from db import *
from app import app
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from modules.utils import *

@db_session()
def layout(start,end):
    start = Poses[start]
    end = Poses[end]
    output = [
        dcc.Store(id='transition-info',data={'start':start.index,'end':end.index}),
        html.H1(f'{start.name} to {end.name} Transitions:')
        ]
    elegible_transitions = select(i for i in Transitions if i.start==start and i.end==end and i.approved==True)
    if len(elegible_transitions)==0:
        output.append(
            html.Div(
                'No Transitions Found in Database',
                style={'text-align':'center','margin-top':'1em'}
            ))
    else:
        for transition in elegible_transitions:
            output.append(show_video(transition.index,show_title=False))
    contribute_form = [
        html.H2(f'Add your own transition:'),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label('Youtube ID'),
                        dbc.Input(id='youtube-id')
                    ]
                ),
                dbc.Col(
                    [   
                        dbc.Button('SUBMIT',style={'margin-top':'2em'},id='submit-transition')
                    ]
                )
                
            ],
            style = {'margin':'0 auto'}
        ),
        html.Div(id='add-feedback')
    ]
    return html.Div(output + contribute_form,style={'width':'80%','margin':'0 auto'})

@app.callback(
    Output('add-feedback','children'),
    [Input('submit-transition','n_clicks')],
    [State('youtube-id','value'),State('transition-info','data')]
)
def add_transition(click,youtube_id,transition_data):
    if click is not None:
        with db_session:
            start = transition_data['start']
            end = transition_data['end']
            new_transition = Transitions(start=Poses[start],end=Poses[end],index=youtube_id,approved=True)
            db.commit()
            return 'Transition Added Succesfully. Refresh Page to See Changes'
    return None
