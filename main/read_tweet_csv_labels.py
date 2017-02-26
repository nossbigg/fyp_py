from controller.config import Config
from controller.database_service import DatabaseService
from controller.tweet_csv_label_service import TweetCSVLabelService

config = Config()
dbs = DatabaseService(config)

tcls = TweetCSVLabelService(dbs, config)
tcls.import_csv_label_docs(True)
