from controller.data_import_utils import *
from controller.database_utils import *


class DataImportService:
    """
    Finds and imports gzipped data sources into database
    """

    config = None
    dbclient = None

    def __init__(self, database_service_class, config_class):
        """
        Initialize the Data Import Service.

        :param config_class: Accepts a ConfigParser object.
        """
        self.dbclient = database_service_class
        self.config = config_class

    def import_from_all_dir(self, overwrite=False):
        """

        :param overwrite:
        :return:
        """
        db = self.dbclient.get_db()
        CORPUS_DIR = self.config.get_corpus_dir()

        # list available sources
        import_dirs = os.listdir(CORPUS_DIR)
        import_dirs = [os.path.join(CORPUS_DIR, path) for path in import_dirs]
        import_dirs = [path for path in import_dirs if os.path.isdir(path)]

        # if not overwriting, import only
        if not overwrite:
            existing_collections = db.collection_names()
            existing_collections = {collection_name: "" for collection_name in existing_collections}

            import_dirs = [path for path in import_dirs if
                           get_collectionname_from_source_path(path) not in existing_collections]

        # import sources
        for path in import_dirs:
            self.import_from_dir(path, overwrite)

        # return imported sources
        return import_dirs

    def import_from_dir(self, path, overwrite=False):
        """

        :param path:
        :param overwrite:
        :return:
        """
        db = self.dbclient.get_db()
        collection_name = get_collectionname_from_source_path(path)

        # if collection exists and overwrite is true, remove existing collection
        if collection_name in db.collection_names():
            if overwrite:
                db[collection_name].drop()
            else:
                return

        # import gzip archives
        archives_json = []
        archives_paths = get_archives_from_path(path)
        for file_path in archives_paths:
            try:
                archives_json.extend(get_json_from_archive_file(file_path))
            except IOError:
                pass

        # get tweets from archives
        tweets = get_tweets_from_archives(archives_json)

        # convert date format to mongo-compatible
        tweets = convert_tweets_date(tweets)

        # store tweets
        db[collection_name].insert(list(tweets.values()))

# TODO consider incremental addition from files (ie. have to check for duplicates)
