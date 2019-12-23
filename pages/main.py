from db import *
from app import app
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from modules.utils import *

def layout():
    return html.Div([
            html.H1('Acro Flow Generator',style={'text-align':'center','margin-top':'1em'}),
            dcc.Markdown('''
            Welcome to the acro flow generator. This app can be used to discover transitions that can be chained together to make flows or washing machines.
            [Click Here](/transitions) To view and contribute to our library of transitions.
            ''',
                style={'margin':'0 auto'}
            ),
            html.Div(
                id='flow-content'
            ),
            html.Div(
                children=[
                    html.H3('Pick Starting Transition:',id='control-instructions'),
                    dcc.Dropdown(
                        id='move-selection',
                        options = get_options(None),
                        value='random',
                        placeholder = 'select next move'
                    ),
                    dbc.ButtonGroup(
                        [
                            dbc.Button('GET NEXT', color='primary',id='submit',size='lg'),
                            dbc.Button('REMOVE PREVIOUS',color='secondary',id='remove',size='lg'),
                            dbc.Button('START OVER',color='danger',id='restart',size='lg'),
                        ],
                        id = 'actions',
                        style={'width':'100%','margin-top':'1em'}
                    )
                ],
                id='controls'
            ),
            dcc.Store(id='flow-state',data={'transitions':[],'submit_clicks':0,'restart_clicks':0,'remove_clicks':0}),
            # dcc.Store(id='control-state',data={'transitions':[]})
        ],
        style={'width':'80%','margin':'0 auto'}
        )

@app.callback(
    Output('flow-content','children'),
    [Input('flow-state','data')]
)
def show_flow(flow_state):
    videos = [show_video(i['id']) for i in flow_state['transitions']]
    return videos

@app.callback(
    Output('flow-state','data'),
    [Input('submit','n_clicks'),
    Input('restart','n_clicks'),
    Input('remove','n_clicks')],
    [State('flow-state','data'),
    State('move-selection','value')]
)
def update_flow(submit,restart,remove,state,pose):
    with db_session:
        if submit is not None:
            if state['submit_clicks']<submit:
                print(pose)
                if pose=='random' or pose == None:
                    if len(state['transitions'])>0:
                        previous = Transitions[state['transitions'][-1]['id']]
                        elegible_transitions = select(i for i in Transitions if i.start == previous.end and i!=previous)
                    else:
                        elegible_transitions = select(i for i in Transitions)
                else:
                    if len(state['transitions'])>0:
                        previous = Transitions[state['transitions'][-1]['id']]
                        elegible_transitions = select(i for i in Transitions if i.end==Poses[int(pose)] and i.start == previous.end and i!=previous)
                    else: 
                        elegible_transitions = select(i for i in Transitions if i.end==Poses[int(pose)])
                transition = elegible_transitions.random(1)
                alternate = len(elegible_transitions)>1 and pose!='random'
                if len(transition)>0:
                    state['transitions'].append({'alternate':alternate ,'id':transition[0].index})
                    state['submit_clicks'] = submit
        if restart is not None:
            if state['restart_clicks']<restart:
                state['transitions'] = []
                state['restart_clicks'] = restart
        if remove is not None:
            if state['remove_clicks']<remove:
                state['transitions'].pop()
                state['remove_clicks'] = remove
        print(state)
        return state

@app.callback(
    Output('remove','style'),
    [Input('flow-state','data')]
)
def show_remove(data):
    if len(data['transitions'])==0:
        return {'display':'none'}
    return {}

@app.callback(
    Output('restart','style'),
    [Input('flow-state','data')]
)
def show_restart(data):
    if len(data['transitions'])==0:
        return {'display':'none'}
    return {}

@app.callback(
    Output('submit','children'),
    [Input('flow-state','data')]
)
def update_submit(data):
    if len(data['transitions'])==0:
        return 'GET FIRST'
    return 'GET NEXT'

@app.callback(
    Output('control-instructions','children'),
    [Input('flow-state','data')]
)
def update_instructions(data):
    if len(data['transitions'])==0:
        return 'Pick Starting Position:'
    return 'Pick Next Position:'

@app.callback(
    Output('move-selection','options'),
    [Input('flow-state','data')]
)
def update_options(state):
    with db_session:
        if len(state['transitions'])==0:
            return get_options(None)
        else:
            previous = Transitions[state['transitions'][-1]['id']].end.index
            return get_options(previous)


def get_options(previous):
    with db_session:
        if previous==None:
            all_poses = select(i.start for i in Transitions)
        else:
            all_poses = select(i.end for i in Transitions if i.start.index==previous)
        return [{'label':'Random','value':'random'}]+[{'label':pose.name,'value':pose.index} for pose in all_poses]