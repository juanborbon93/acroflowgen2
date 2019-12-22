from pony.orm import *

db = Database()

class Transitions(db.Entity):
    start = Required(str,column='start')
    end = Required(str,column='end')
    index = PrimaryKey(str,column='id',auto=True)