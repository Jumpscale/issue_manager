from playhouse.sqlite_ext import SqliteExtDatabase

class IndexInfo:
    def __init__(self):

        self._indexDB = None
        self.indexDBPath = "/tmp/index.db"

    @property
    def indexDB(self):
        if self._indexDB is None:
            self._indexDB = SqliteExtDatabase(self.indexDBPath)
        return self._indexDB

indexinfo = IndexInfo()