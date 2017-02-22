from controller.config import Config
from controller.data_import_service import DataImportService
from controller.database_service import DatabaseService

config = Config()
dbs = DatabaseService(config)
dis = DataImportService(dbs, config)

# add archives into db (overwrite setting)
dis.import_from_all_dir(True)
# dis.import_from_all_dir()

pass
