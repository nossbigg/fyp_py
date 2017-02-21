from ConfigParser import ConfigParser


def init_config():
  parser = ConfigParser()
  parser.read('config.ini')
  return parser


class Config:
  config = init_config()
