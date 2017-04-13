from controller.config import Config
from controller.database_service import DatabaseService
from controller.tweet_csv_label_service import TweetCSVLabelService

config = Config()
dbs = DatabaseService(config)

collection_names = ['sickhillary', 'baghdadi_dead', 'death_hoax',
                    'mosul_battle', 'us_economic_policy', 'trump_cabinet']

tcls = TweetCSVLabelService(dbs, config)
for c in collection_names:
    tcls.export_csv_label_doc(c)
