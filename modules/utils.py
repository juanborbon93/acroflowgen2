from db import *
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
# from dash_dangerously_set_inner_html import DangerouslySetInnerHTML as raw_html


@db_session()
def show_video(transition,show_title=True):
    db_transition = Transitions[transition['id'],transition['start time']]
    start = db_transition.start.name
    end = db_transition.end.name
    youtube_id = transition['id']
    start_time = db_transition.starttime
    end_time = db_transition.endtime
    if start_time==0 and end_time==0:
        src = f"https://www.youtube.com/embed/{youtube_id}?rel=0"
    else:
        src = f"https://www.youtube.com/embed/{youtube_id}?start={start_time}&end={end_time}&loop=1&autoplay=0&playlist={youtube_id}"
    video = html.Div([
        html.Iframe(
                src= src,
                style={
                    'position': 'absolute',
                    'top': '0',
                    'left': '0',
                    'width': '100%',
                    'height': '100%'
                }
            )
        # raw_html(
        #     f'''
        #     <iframe src="{src}" allow='autoplay'></iframe>
        #     '''
        # )
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

@db_session()
def get_pose_options(include_all=True):
    all_poses = select(i for i in Poses)
    all_poses = [{'label':pose.name,'value':pose.index} for pose in all_poses]
    if include_all:
        return [{'label':'All','value':'All'}]+all_poses
    else: 
        return all_poses