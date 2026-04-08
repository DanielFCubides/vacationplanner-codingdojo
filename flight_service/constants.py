import os
import configparser

config = configparser.ConfigParser()
config.read('conf.ini')

root_path = os.path.dirname(__file__)
presentation_path = os.path.join(root_path, 'presentations')
