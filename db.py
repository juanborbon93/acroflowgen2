from modules.database import *
import os


username=os.environ['USER']
password=os.environ['PASSWORD']
host=os.environ['HOST']
port=os.environ['PORT']
database=os.environ['DATABASE']
ssl=os.environ['DBSSL']

db.bind(provider='postgres', user=username, password=password, host=host ,port=port, database=database, sslmode=ssl)
db.generate_mapping(create_tables=False)
