import time

import faker


def stream():
    for i in range(20):
        fake = faker.Faker()
        name = fake.name()
        time.sleep(1)
        yield str(name).decode('utf-8')
