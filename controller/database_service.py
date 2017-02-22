import pymongo


class DatabaseService:
    dbclient = None
    config = None

    def __init__(self, config_class):
        self.config = config_class
        self.dbclient = pymongo.MongoClient()

    def get_db(self, db_name=None):
        if db_name is None:
            db_name = self.config.get_db_name()

        return self.dbclient[db_name]

    def get_collection_names(self, db_name=None):
        if db_name is None:
            db_name = self.config.get_db_name()

        return self.dbclient[db_name].collection_names()
