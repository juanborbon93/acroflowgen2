from pony.orm import *

db = Database()

class Transitions(db.Entity):
    start = Required('Poses',column='start',reverse='starting_pose')
    end = Required('Poses',column='end',reverse='ending_pose')
    index = PrimaryKey(str,column='id')
    approved = Required(bool,column='approved')

class Poses(db.Entity):
    index = PrimaryKey(int,column='id',auto=True)
    name = Required(str,column='name')
    starting_pose = Set('Transitions',reverse='start')
    ending_pose = Set('Transitions',reverse='end')
    