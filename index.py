import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from waitress import serve
from pony import orm
from app import app,server
from db import *


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='main-page')
])
    
def app_layout(view_type):
    if view_type == 'main':
        layout = html.Div([
            html.H1('Acro Flow Generator',style={'text-align':'center','margin-top':'1em'}),
            dcc.Markdown('''
            Welcome to the acro flow generator. This app can be used to discover transition that can be chained together to make flows or washing machines.
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
    return layout

@app.callback(
    Output('main-page','children'),
    [Input('url','pathname')]
)
def show_page(pathname):
    if pathname == None:
        return None
    if pathname == '/':
        return app_layout('main')
    pathname = pathname.split('/')
    if  pathname[0:2] == ['','flowview']:
        return app_layout('flowview')
    if  pathname[0:2] == ['','admin']:
        return app_layout('admin')

@app.callback(
    Output('flow-content','children'),
    [Input('flow-state','data')]
)
def show_flow(flow_state):
    videos = [show_video(i) for i in flow_state['transitions']]
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
                        previous = Transitions[state['transitions'][-1]['id']].end
                        elegible_transitions = select(i for i in Transitions if i.start == previous)
                    else:
                        elegible_transitions = select(i for i in Transitions)
                else:
                    elegible_transitions = select(i for i in Transitions if i.end==Poses[int(pose)])
                transition = elegible_transitions.random(1)
                alternate = len(elegible_transitions)>1 and pose!='random'
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

@db_session()
def show_video(transition):
    start = Transitions[transition['id']].start.name
    end = Transitions[transition['id']].end.name
    youtube_id = transition['id']
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
    return html.Div(
        [
            html.H2(f'{start} to {end}'),
            video
        ]
    )
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

if __name__ == '__main__':
    # app.server.run(host='0.0.0.0', port=5000,debug=True) 
    # app.run_server()
    serve(server,host='0.0.0.0', port=5000)
