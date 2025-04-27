import json
import time

import faker

faker = faker.Faker()


def stream():
    for i in range(20):
        name = faker.name()
        print(name)
        time.sleep(1)
        yield f"{name}\n"
