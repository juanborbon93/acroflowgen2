from db import *
from app import app
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State


def get_pose_options():
    with db_session:
        all_poses = select(i for i in Poses)
        return [{'label':'All','value':'All'}]+[{'label':pose.name,'value':pose.index} for pose in all_poses]

layout = html.Div(
    [
        html.H1('Transition Table',style={'text-align':'center','margin-top':'1em'}),
        html.H3('Starting Position Filter:'),
        dcc.Dropdown(options=get_pose_options(),value='All',id='start-filter'),
        html.H3('Ending Position Filter:'),
        dcc.Dropdown(options=get_pose_options(),value='All',id='end-filter'),
        dbc.Button('GET TRANSITION LIST',id='get-transitions',block=True),
        dcc.Loading(id='transition-table')
    ],
    style={'width':'80%','margin':'0 auto'}
)

@app.callback(
    Output('transition-table','children'),
    [Input('get-transitions','n_clicks')],
    [State('start-filter','value'),State('end-filter','value')]
)
def generate_table(click,start_filter,end_filter):
    if click is not None:
        return transition_table(start_filter,end_filter)
    else:
        return None


@db_session()
def transition_table(starting,ending):
    poses = select(i for i in Poses)
    transition_list = []
    for start in poses:
        if start.index==starting or starting=='All':
            for end in poses:
                if start!=end and (ending=='All' or end.index==ending):
                    existing_transitions_count = select(i for i in Transitions if i.start==start and i.end == end and i.approved==True).count()
                    transition_list.append(
                        {
                            'start':{
                                'name':start.name,
                                'id':start.index
                            },
                            'end':{
                                'name':end.name,
                                'id':end.index
                            },
                            'transitions':{
                                'amount':existing_transitions_count,
                                # 'list':[i.index for i in existing_transitions]
                            }
                        }
                    )
    table_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th('Start'),
                    html.Th('End'),
                    html.Th('Existing Transitions'),
                    # html.Th('Contribute Link')
                ]
            )
        )
    ]
    table_body = []
    for transition in transition_list:
        table_body.append(
            html.Tr(
                [
                    html.Td(transition['start']['name']),
                    html.Td(transition['end']['name']),
                    html.Td(transition['transitions']['amount']),
                    html.Td(
                        html.A(
                            dbc.Button('View / Contribute'),
                            href = f'/view_contribute/{transition["start"]["id"]}&{transition["end"]["id"]}',
                            target = '_blank'
                        )
                    )
                ]
            )
        )
    table = dbc.Table(table_header+table_body,bordered=True)
    return table
        