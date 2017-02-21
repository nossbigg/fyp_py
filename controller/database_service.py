import pymongo


class DatabaseService:
    dbclient = None
    config = None

    def __init__(self, config_class):
        self.config = config_class
        self.dbclient = pymongo.MongoClient()

    def get_db(self, dbName=None):
        if dbName == None:
            dbName = self.config.get_db_name()

        return self.dbclient[dbName]
