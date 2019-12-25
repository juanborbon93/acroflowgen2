from db import *
from app import app
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from modules.utils import *
from datetime import datetime

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
            output.append(show_video({'id':transition.index,'start time':transition.starttime},show_title=False))
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
                        dbc.Label('Start Time (seconds)'),
                        dbc.Input(id='start-time',type='number',step=1)
                    ],
                    style={'display':'none'}
                ),
                dbc.Col(
                    [
                        dbc.Label('End Time (seconds)'),
                        dbc.Input(id='end-time',type='number',step=1)
                    ],
                    style={'display':'none'}
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
    [
        State('youtube-id','value'),
        State('start-time','value'),
        State('end-time','value'),
        State('transition-info','data')
    ]
)
def add_transition(click,youtube_id,start_time,end_time,transition_data):
    if click is not None:
        if start_time==None and end_time==None:
            start_time=0
            end_time=0
        if start_time>end_time:
            return 'INPUT ERROR: CHECK START TIME AND END TIME'
        with db_session:
            start = transition_data['start']
            end = transition_data['end']
            new_transition = Transitions(
                start=Poses[start],
                end=Poses[end],
                index=youtube_id,
                approved=True,
                starttime=start_time,
                endtime=end_time,
                createdate=datetime.utcnow())
            db.commit()
            return 'Transition Added Succesfully. Refresh Page to See Changes'
    return None
