import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder
from app.index import MyIndexView
from .momentjs import momentjs

"""
 Logging configuration
"""

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.globals['momentjs'] = momentjs

db = SQLA(app)
appbuilder = AppBuilder(app, db.session, indexview=MyIndexView, base_template='mybase.html')


"""
from sqlalchemy.engine import Engine
from sqlalchemy import event

#Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""    

from app import views

