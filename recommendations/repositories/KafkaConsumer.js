import { Kafka } from 'kafkajs';

export {init};
let kafka = new Kafka({
    clientId: "my-app",
    brokers: ["localhost:9092"],
});


async function init() {
    let group = "node-app";
    const consumer = kafka.consumer({ groupId: group });
    await consumer.connect();

    await consumer.subscribe({ topics: ["search-params"], fromBeginning: false });

    await consumer.run({
        eachMessage: async ({ topic, partition, message, heartbeat, pause }) => {
            console.log(
                `${group}: [${topic}]: PART:${partition}: hb ${heartbeat}`,
                message.value.toString()
            );
        },
    });
}