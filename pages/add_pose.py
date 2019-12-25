from db import *
from app import app
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from modules.utils import *

def layout():
    output = [
        html.H1('Add a Pose to Library',style={'text-align':'center','margin-top':'1em'}),
        dcc.Markdown(
            '''
            ### Instructions:
            - Take a look at the list of transitions contained in the drop-down menu. 
            - If you can't find the pose you are looking for you can submit a new one.
            - Enter capitalized pose name (example: "Hand to Hand" not "hand to hand")
            - You may want to specify if the pose is L-base or Standing in the name
            - Click Submit
            '''
        ),
        dcc.Dropdown(
            options=get_pose_options(include_all=False),
            id='existing-poses'
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label('Pose Name'),
                        dbc.Input(id='pose-name')
                    ]
                ),
                dbc.Col(
                    [   
                        dbc.Button('SUBMIT POSE',style={'margin-top':'2em'},id='submit-pose')
                    ]
                )
                
            ],
            style = {'margin':'0 auto'}
        ),
        html.Div(id='add-pose-feedback')
    ]
    return html.Div(output,style={'width':'80%','margin':'0 auto'})

@app.callback(
    [Output('add-pose-feedback','children'),Output('existing-poses','options')],
    [Input('submit-pose','n_clicks')],
    [State('pose-name','value')]
)
def submit_pose(click,pose_name):
    if click is not None: 
        if pose_name is None:
            return 'Please Enter a Pose Name',get_pose_options(include_all=False)
        else: 
            with db_session:
                new_pose = Poses(name=pose_name)
                db.commit()
            return f"{pose_name} was added.",get_pose_options(include_all=False)
    else:
        return None,get_pose_options(include_all=False)
