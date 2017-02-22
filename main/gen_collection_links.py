from controller.config import Config
from controller.tweet_links_service import TweetLinksService
from controller.database_service import DatabaseService
from controller.database_utils import get_tweet_collections_only

config = Config()
dbs = DatabaseService(config)

db = dbs.get_db()
collection_names = get_tweet_collections_only(db.collection_names())

dls = TweetLinksService(dbs, config)
dls.gen_all_collection_links()

pass
