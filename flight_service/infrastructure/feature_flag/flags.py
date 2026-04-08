from openfeature import api
from openfeature.provider.in_memory_provider import InMemoryProvider

from infrastructure.feature_flag.memory_provider import WELCOME_MESSAGE_FLAG, my_flags

api.set_provider(InMemoryProvider(my_flags))

feature_flag_client = api.get_client()

flag_value = feature_flag_client.get_boolean_value(WELCOME_MESSAGE_FLAG, False)
