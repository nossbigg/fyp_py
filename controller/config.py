from ConfigParser import ConfigParser
from os.path import dirname, abspath

DEFAULT_CONFIG_FILE_PATH = '../config/config.ini'
ROOT_DIR = dirname(dirname(abspath(__file__)))


class Config:
    config_var = None

    def __init__(self, config_file_path=DEFAULT_CONFIG_FILE_PATH):
        parser = ConfigParser()
        parser.read(config_file_path)

        self.config_var = parser

    def get_corpus_dir(self):
        return self.config_var.get('CORPUS', 'CORPUS_DIR')

    def get_db_name(self):
        return self.config_var.get('DB-MONGO', 'DB_NAME')

    def get_tweet_csv_label_dir(self):
        return self.config_var.get('CORPUS', 'TWEET_CSV_LABEL_DIR')

    @staticmethod
    def get_root_dir(self):
        return ROOT_DIR
