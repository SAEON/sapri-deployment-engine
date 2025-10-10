import configparser

CONFIG_FILE_PATH = './config/config.ini'

config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
