import express from 'express';
import {GetSearchParams, readFromRedis} from "../repositories/SearchParamsRepository.js";
const app = express()
const port = 3000

export function InitializeRest() {
    app.get('/', (req, res) => {
        res.send('Hello World!')
        GetSearchParams().then(r => console.info(r));

    })

    app.listen(port, () => {
        console.log(`Example app listening on port ${port}`)
        readFromRedis();
    })
}