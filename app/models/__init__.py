# For default, sqlite db should be at the root of the project.
from os import getenv
from uuid import uuid4


DB_PATH = getenv('TODO_DB_PATH', 'todo.db')
IP = getenv('TODO_IP', 'localhost')
PORT = getenv('TODO_PORT', '8080')

def create_uuid():
    return str(uuid4()).replace('-', '')