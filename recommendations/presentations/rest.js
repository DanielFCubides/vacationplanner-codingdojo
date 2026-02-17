import express from 'express';
import { GetSearchParams, GetSearchParams2, readFromRedis } from "../repositories/SearchParamsRepository.js";
import { init } from "../repositories/KafkaConsumer.js";
const app = express()
const port = 3000

export function InitializeRest() {
    app.get('/', (req, res) => {
        res.send('getting messages from queue')
        GetSearchParams().then(r => console.info(r));

    })

    app.get('/subscribe/', (req, res) => {
        res.send('getting messages from subscription')
        GetSearchParams2().then(r => console.info(r));

    })

    app.get('/kafka/', (req, res) => {
        res.send('getting messages from subscription')
        init().then(r => console.info(r));

    })

    app.listen(port, () => {
        console.log(`Example app listening on port ${port}`)
        readFromRedis();
    })
}