from sqlite3 import connect
from threading import Lock

class LockableSqliteConnection(object):
    def __init__(self, dburi):
        self.lock = Lock()
        self.connection = connect(dburi, uri=True, check_same_thread=False)
        self.cursor = None
    def __enter__(self):
        self.lock.acquire()
        self.cursor = self.connection.cursor()
        return self
    def __exit__(self, type, value, traceback):
        self.connection.commit()
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None
        self.lock.release()
