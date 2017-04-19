import os
from db import get_rc
from rq import Worker, Queue, Connection

listen = ['default']

conn = get_rc()
if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()