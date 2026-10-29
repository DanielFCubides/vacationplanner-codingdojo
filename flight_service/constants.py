import os
import configparser

config = configparser.ConfigParser()
config.read('conf.ini')

# Allow deployment/runtime configuration to override the checked-in defaults.
for section, key, env_name in (
    ('Redis', 'host', 'REDIS_HOST'),
    ('Redis', 'port', 'REDIS_PORT'),
    ('Kafka', 'host', 'KAFKA_HOST'),
    ('Kafka', 'port', 'KAFKA_PORT'),
    ('Default', 'repository', 'FLIGHT_REPOSITORY'),
    ('Default', 'publisher', 'FLIGHT_PUBLISHER'),
):
    if value := os.getenv(env_name):
        config[section][key] = value

root_path = os.path.dirname(__file__)
presentation_path = os.path.join(root_path, 'presentations')
