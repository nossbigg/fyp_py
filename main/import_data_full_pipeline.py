from controller.config import Config
from controller.data_import_service import DataImportService
from controller.data_label_service import DataLabelService
from controller.database_service import DatabaseService
from controller.tweet_links_service import TweetLinksService

config = Config()
dbs = DatabaseService(config)

# Import data into db
dis = DataImportService(dbs, config)
dis.import_from_all_dir(True)

# Label tweet type
dls = DataLabelService(dbs, config)
dls.set_all_tweets_type()

# Generate tweet parent links
tls = TweetLinksService(dbs, config)
tls.gen_all_collection_links(True)

# Label tweet text sentiments
dls.set_all_sentiments()


