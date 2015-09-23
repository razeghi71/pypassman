from peewee import *


db = SqliteDatabase('apps.db', threadlocals=True)

class BaseModel(Model):
    class Meta:
        database = db

class App(BaseModel):
    executable = CharField()
    exec_hash = CharField()

class SavedInfo(BaseModel):
    username = CharField()
    password = CharField()
    app = ForeignKeyField(App)

# db = SqliteDatabase('apps.db', threadlocals=True)
# db.connect()
# db.create_tables([App, SavedInfo])