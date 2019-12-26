import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from waitress import serve
from pony import orm
from app import app,server
from db import *
from pages import transition_table, main, view_contribute, add_pose, share

app.title='Acro Flow Generator'


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='main-page',style={'margin-bottom':'2em'})
])

@app.callback(
    Output('main-page','children'),
    [Input('url','pathname')]
)
def show_page(pathname):
    if pathname == None:
        return None
    if pathname == '/':
        return main.layout()
    print('whole path:',pathname)
    pathname = pathname.split('/')
    if  pathname[0:2] == ['','flowview']:
        return app_layout('flowview')
    if  pathname[0:2] == ['','view_contribute'] and len(pathname)==3:
            transition = pathname[-1].split('&')
            if len(transition)==2:
                start = int(transition[0])
                end = int(transition[1])
                return view_contribute.layout(start,end)
    if  pathname[0:2] == ['','transitions'] and len(pathname)==2:
        return transition_table.layout
    if  pathname[0:2] == ['','add_pose'] and len(pathname)==2:
        return add_pose.layout()
    if  pathname[0:2] == ['','share'] and len(pathname)==3:
        # print('whole path:',pathname)
        return share.layout(pathname[-1])
    return html.H1(404)

if __name__ == '__main__':
    # app.server.run(host='0.0.0.0', port=5000,debug=True) 
    app.run_server(host='0.0.0.0', port=5000)
    # app.run_server()
    # serve(server,host='0.0.0.0', port=5000)
