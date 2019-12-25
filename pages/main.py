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
            ## About:
            Welcome to the acro flow generator. This app can be used to discover transitions that can be chained together 
            to make flows or washing machines. I made this tool because I think acro becomes really fun when one discovers how to flow between different poses.
            My hope is that you find this tool useful for choreographing performances, planning classes, or discovering new skills to work on.
            **Please use this app responsibly. Only attempt moves that you can perfom safely!**. 
            ## How to Contribute: 
            This app went live very recently (Dec 2019) and I need help expanding the transition library to make it more complete. 
            Some of the videos you will see are slices of videos I found on YouTube, which serve as temporary placeholders to demonstrate
            the functionality of the app. These placeholders will gradually be replaced with videos submitted by a community of contributors.
            If you would like to contribute to our library of transition videos [**CLICK HERE**](/transitions).

            #### Questions/Concerns? email me: [contact@juanborbon.com](mailto:contact@juanborbon.com)
            ''',
                style={'margin':'0 auto'}
            ),
            html.Div(
                id='flow-content'
            ),
            html.Div(
                children=[
                    dbc.Button('SEE ALTERNATE TRANSITION',block=True,id='see-alternate'),
                    html.H3('Pick Starting Transition:',id='control-instructions',style={'margin-top':'1em'}),
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
            dcc.Store(
                id='flow-state',
                data={
                    'transitions':[],
                    'submit_clicks':0,
                    'restart_clicks':0,
                    'remove_clicks':0,
                    'alternate_clicks':0,
                    'dead_end':False
                    }
            ),
            # dcc.Store(id='control-state',data={'transitions':[]})
        ],
        style={'width':'80%','margin':'0 auto'}
        )


@app.callback(
    [
        Output('see-alternate','children'),
        Output('see-alternate','style')
    ],
    [
        Input('flow-state','data')
    ]
)
def toggle_alternate(state):
    if len(state['transitions'])>0:
        last_transition = state['transitions'][-1]
        if last_transition['alternate']==True:
            with db_session:
                last_transition = state['transitions'][-1]
                last_transition = Transitions[last_transition['id'],last_transition['start time']]
                last_start = last_transition.start.name.upper()
                last_end = last_transition.end.name.upper()
                button_message = f'SEE ALTERNATE TRANSITION FOR {last_start} TO {last_end}'
                style = {'display':'block'}
                return button_message,style
    return '',{'display':'none'}
        

@app.callback(
    Output('flow-content','children'),
    [Input('flow-state','data')]
)
def show_flow(flow_state):
    videos = [show_video({'id':i['id'],'start time':i['start time']}) for i in flow_state['transitions']]
    return videos

@app.callback(
    Output('flow-state','data'),
    [Input('submit','n_clicks'),
    Input('restart','n_clicks'),
    Input('remove','n_clicks'),
    Input('see-alternate','n_clicks')],
    [State('flow-state','data'),
    State('move-selection','value')]
)
def update_flow(submit,restart,remove,alternate_click,state,pose):
    with db_session:
        print(state)
        if submit is not None:
            if state['submit_clicks']<submit:
                print(pose)
                if pose=='random' or pose == None:
                    if len(state['transitions'])>0:
                        previous = Transitions[state['transitions'][-1]['id'],state['transitions'][-1]['start time']]
                        elegible_transitions = select(i for i in Transitions if i.start == previous.end and i!=previous)
                    else:
                        elegible_transitions = select(i for i in Transitions)
                else:
                    if len(state['transitions'])>0:
                        previous = Transitions[state['transitions'][-1]['id'],state['transitions'][-1]['start time']]
                        elegible_transitions = select(i for i in Transitions if i.end==Poses[int(pose)] and i.start == previous.end and i!=previous)
                    else: 
                        elegible_transitions = select(i for i in Transitions if i.start==Poses[int(pose)])
                    
                transition = elegible_transitions.random(1)
                alternate = len(elegible_transitions)>1 and pose!='random'
                if len(transition)>0:
                    transition_end = transition[0].end
                    compatible_starts = select(i for i in Transitions if i.start == transition_end and i!=transition[0]).count()
                    dead_end = compatible_starts == 0
                    state['transitions'].append(
                        {
                            'alternate':alternate ,
                            'id':transition[0].index,
                            'start time':transition[0].starttime,
                            'dead end':dead_end
                        }
                    )
                    state['submit_clicks'] = submit
        if restart is not None:
            if state['restart_clicks']<restart:
                state['transitions'] = []
                state['restart_clicks'] = restart
        if remove is not None:
            if state['remove_clicks']<remove:
                state['transitions'].pop()
                state['remove_clicks'] = remove
        if alternate_click is not None and len(state['transitions'])>0:
            if state['alternate_clicks']<alternate_click and state['transitions'][-1]['alternate']==True:
                state['alternate_clicks']=alternate_click
                state['transitions'][-1] = get_alternate(state['transitions'][-1])
        print(state)
        return state

@db_session()
def get_alternate(transition):
    transition_id = transition['id']
    db_transition = Transitions[transition_id,transition['start time']]
    potential_alternates = select(i for i in Transitions if i.start==db_transition.start and i.end==db_transition.end and i.index!=db_transition.index)
    is_alternate = len(potential_alternates)>0
    if is_alternate:
        transition_id = potential_alternates.random(1)[0].index
    transition = {'alternate':is_alternate,'id':transition_id}
    return transition

# change how the controls of the page look like based on the flow-state
@app.callback(
    [
        Output('remove','style'),
        Output('restart','style'),
        Output('submit','style'),
        Output('submit','children'),
        Output('control-instructions','children'),
    ],
    [Input('flow-state','data')]
)
def controls_display(data):
    submit_display = {}
    if len(data['transitions'])==0:
        remove_display = {'display':'none'}
        restart_display = {'display':'none'}
        submit_message = 'GET FIRST'
        control_instructions = 'Pick Starting Position:'
    else:
        remove_display =  {}
        restart_display =  {}
        submit_message = 'GET NEXT'
        control_instructions = 'Pick Next Position:'
        last_transition = data['transitions'][-1]
        if last_transition['dead end']==True:
            with db_session:
                db_last_transition = Transitions[last_transition['id'],last_transition['start time']]
                last_end = db_last_transition.end.name
                control_instructions = f'Woops... no transition starting in {last_end} exist in the database.'
                submit_display = {'display':'none'}
                
        
    
    return remove_display,restart_display,submit_display,submit_message,control_instructions 
    

@app.callback(
    Output('move-selection','options'),
    [Input('flow-state','data')]
)
def update_options(state):
    with db_session:
        if len(state['transitions'])==0:
            return get_options(None)
        else:
            previous = Transitions[state['transitions'][-1]['id'],state['transitions'][-1]['start time']].end.index
            return get_options(previous)


def get_options(previous):
    with db_session:
        if previous==None:
            all_poses = select(i.start for i in Transitions)
        else:
            all_poses = select(i.end for i in Transitions if i.start.index==previous)
        return [{'label':'Random','value':'random'}]+[{'label':pose.name,'value':pose.index} for pose in all_poses]