from controller.config import Config
from controller.data_label_service import DataLabelService
from controller.database_service import DatabaseService

config = Config()
dbs = DatabaseService(config)
dls = DataLabelService(dbs, config)

dls.set_all_sentiments()

pass
